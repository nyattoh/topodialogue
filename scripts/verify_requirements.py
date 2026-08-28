#!/usr/bin/env python3
"""Adversarial, offline checks for the H2O Memory requirements HTML.

The checked HTML is intentionally not modified.  ``--negative`` creates
short-lived copies beside it with required evidence removed and asserts that
the corresponding checks fail.  The checker uses only the Python standard
library so it can run in a clean repository checkout.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_TARGET = Path("docs/tasks/54df411b/requirements-definition.html")
VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


class StructureParser(HTMLParser):
    """Small HTML structure reader with strict tag-balance diagnostics."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.start_tags: list[tuple[str, dict[str, str | None]]] = []
        self.end_tags: list[str] = []
        self.comments: list[str] = []
        self.doctypes: list[str] = []
        self.text: list[str] = []
        self.inline_styles: list[str] = []

    def handle_decl(self, decl: str) -> None:
        if decl.lower().startswith("doctype"):
            self.doctypes.append(decl)

    def handle_comment(self, data: str) -> None:
        self.comments.append(data)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized = tag.lower()
        attr_map = {key.lower(): value for key, value in attrs}
        self.start_tags.append((normalized, attr_map))
        if normalized not in VOID_ELEMENTS:
            self.stack.append(normalized)
        if "style" in attr_map and attr_map["style"]:
            self.inline_styles.append(attr_map["style"] or "")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized = tag.lower()
        self.start_tags.append((normalized, {key.lower(): value for key, value in attrs}))

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.lower()
        self.end_tags.append(normalized)
        if normalized in VOID_ELEMENTS:
            self.errors.append(f"closing void element </{normalized}>")
            return
        if not self.stack:
            self.errors.append(f"orphan closing tag </{normalized}>")
            return
        if self.stack[-1] != normalized:
            self.errors.append(
                f"tag mismatch: expected </{self.stack[-1]}> before </{normalized}>"
            )
            # Recover enough to report later independent errors.
            if normalized in self.stack:
                self.stack.remove(normalized)
            return
        self.stack.pop()

    def handle_data(self, data: str) -> None:
        self.text.append(data)

    def handle_entityref(self, name: str) -> None:
        self.text.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.text.append(f"&#{name};")

    def handle_pi(self, data: str) -> None:
        self.errors.append(f"processing instruction is not allowed: {data}")

    def finish(self) -> None:
        if self.stack:
            self.errors.append("unclosed tags: " + ", ".join(self.stack))


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


class VerificationError(Exception):
    pass


def fail(detail: str) -> None:
    raise VerificationError(detail)


def parse_file(path: Path) -> tuple[str, StructureParser]:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"cannot read {path}: {exc}")
    parser = StructureParser()
    try:
        parser.feed(source)
        parser.close()
    except Exception as exc:  # HTMLParser is permissive, but keep this explicit.
        fail(f"HTML parser raised {type(exc).__name__}: {exc}")
    parser.finish()
    return source, parser


def attr_values(parser: StructureParser, key: str) -> list[str | None]:
    return [attrs.get(key) for _, attrs in parser.start_tags if key in attrs]


def section_text(source: str, section_id: str) -> str:
    match = re.search(
        rf'<section\b[^>]*\bid=["\']{re.escape(section_id)}["\'][^>]*>(.*?)</section>',
        source,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        fail(f"missing section id={section_id}")
    return re.sub(r"<[^>]+>", " ", match.group(1))


def check_complete_html(path: Path) -> None:
    source, parser = parse_file(path)
    if not re.match(r"^\s*<!doctype\s+html\s*>", source, flags=re.IGNORECASE):
        fail("first declaration is not <!doctype html>")
    if parser.errors:
        fail("; ".join(parser.errors))
    names = [tag for tag, _ in parser.start_tags]
    for name in ("html", "head", "body", "main"):
        if names.count(name) != 1:
            fail(f"expected exactly one <{name}>, got {names.count(name)}")
    if not re.search(r"<html\b[^>]*\blang=[\"']ja[\"']", source, re.I):
        fail("<html lang=ja> is missing")
    if not re.search(r"<meta\b[^>]*charset=[\"']utf-8[\"']", source, re.I):
        fail("UTF-8 charset declaration is missing")
    if not re.search(r"<title\b[^>]*>.*?</title>", source, re.I | re.S):
        fail("title is missing")
    ids = [value for value in attr_values(parser, "id") if value]
    duplicates = sorted({value for value in ids if ids.count(value) > 1})
    if duplicates:
        fail("duplicate id attributes: " + ", ".join(duplicates))


def check_standalone(path: Path) -> None:
    source, parser = parse_file(path)
    dependency_errors: list[str] = []
    for tag, attrs in parser.start_tags:
        if tag == "link" and (attrs.get("rel") or "").lower() == "stylesheet":
            dependency_errors.append("external stylesheet link")
        if tag in {"script", "img", "iframe", "object", "embed", "video", "audio"}:
            if attrs.get("src") or attrs.get("data") or tag == "script":
                dependency_errors.append(f"external/runtime dependency <{tag}>")
    # SVG marker/filter references such as url(#arrow-blue) are self-contained.
    if re.search(r"@import\s|url\s*\(\s*(?!#)", source, re.I):
        dependency_errors.append("CSS @import/url dependency")
    if dependency_errors:
        fail(", ".join(dependency_errors))
    # Anchor targets are allowed, but local document links must resolve.
    for href in re.findall(r"<a\b[^>]*\bhref=[\"']([^\"']+)", source, re.I):
        parsed = urlparse(href)
        if parsed.scheme or parsed.netloc:
            continue
        if href.startswith("#"):
            if not re.search(rf'\bid=["\']{re.escape(href[1:])}["\']', source):
                fail(f"broken fragment link {href}")
            continue
        target = (path.parent / parsed.path).resolve()
        if not target.is_file():
            fail(f"broken local link {href}")


def check_architecture_attribute(parser: StructureParser) -> None:
    matches = [
        attrs
        for tag, attrs in parser.start_tags
        if tag == "section" and "data-kamui-architecture-proposal" in attrs
    ]
    if len(matches) != 1 or matches[0].get("data-kamui-architecture-proposal") != "true":
        fail("exactly one architecture section must have data-kamui-architecture-proposal=true")


def check_svg(source: str) -> None:
    matches = re.findall(r"<svg\b.*?</svg>", source, re.I | re.S)
    if len(matches) != 1:
        fail(f"expected one inline SVG, got {len(matches)}")
    try:
        ET.fromstring(matches[0])
    except ET.ParseError as exc:
        fail(f"inline SVG/XML parse failed: {exc}")
    if not re.search(r"<title\b", matches[0], re.I) or not re.search(r"<desc\b", matches[0], re.I):
        fail("architecture SVG lacks accessible title/desc")


def check_content(source: str) -> None:
    thesis = section_text(source, "thesis")
    for phrase in ("表現形式", "精度", "物理配置", "一つの「相」", "同時に再構成"):
        if phrase not in thesis:
            fail(f"central thesis missing {phrase}")

    phases = section_text(source, "phases")
    for phase, required in {
        "vapor": ("疎", "低精度", "遠い低コスト層", "構造"),
        "liquid": ("部分展開", "中程度", "DRAM"),
        "ice": ("詳細", "高精度", "HBM", "SRAM", "計算直近"),
    }.items():
        if phase not in phases.lower():
            fail(f"phase {phase} is missing")
        missing = [item for item in required if item.lower() not in phases.lower()]
        if missing:
            fail(f"phase {phase} missing {', '.join(missing)}")
    for operator in ("evaporate", "condense", "freeze", "melt"):
        if operator not in section_text(source, "operators").lower():
            fail(f"operator {operator} is missing")

    skeleton = section_text(source, "skeleton").lower()
    for item in ("connectivity", "revisit", "branch", "attractor-like", "transition order", "provenance"):
        if item not in skeleton:
            fail(f"topology skeleton item {item} is missing")

    metrics = section_text(source, "metrics").lower()
    for item in (
        "hbm occupancy",
        "hbm–dram transfer volume",
        "sram/cache hit rate",
        "bandwidth",
        "latency",
        "total power",
        "fpga",
        "codec",
        "reconstruction fidelity",
        "answer quality",
        "tpr",
    ):
        if item not in metrics:
            fail(f"metric {item} is missing")

    experiment = section_text(source, "experiment")
    for phrase in ("提案実験", "結果値は報告しない", "反証条件", "FPGA"):
        if phrase not in experiment:
            fail(f"experiment boundary missing {phrase}")
    if not re.search(r"未実施|実行していない|実施していない", source):
        fail("document does not mark the proposed experiment as unexecuted")

    evidence = section_text(source, "evidence-boundary")
    for alternatives in (("系統的レビューではない",), ("novelty hypothesis",), ("未実証",), ("primary", "一次情報")):
        if not any(phrase.lower() in evidence.lower() for phrase in alternatives):
            fail(f"citation boundary missing {' / '.join(alternatives)}")
    if re.search(r"新規性を主張する|新規性である|novel(?!ty hypothesis)", evidence, re.I):
        fail("evidence boundary contains an unqualified novelty claim")

    power = section_text(source, "power")
    for term in ("inference-compute", "memory-retention", "inter-memory-transfer", "compression/decompression", "二重計上"):
        if term.lower() not in power.lower():
            fail(f"power boundary missing {term}")

    non_goals = section_text(source, "non-goals")
    for phrase in ("FPGA実験", "multi-agent", "GraphRAG", "persistent homology", "wearable", "治療", "診断", "raw personal dialogue"):
        if phrase.lower() not in non_goals.lower():
            fail(f"non-goal/safety boundary missing {phrase}")


def check_deliverables(source: str, root: Path) -> None:
    deliverables = section_text(source, "deliverables")
    required = (
        "paper/draft6/topodialogue-h2o-en.tex",
        "paper/draft6/topodialogue-h2o-ja.md",
        "paper/draft6/references.bib",
        "paper/draft6/fact-check.md",
        "paper/draft6/README.md",
        "paper/draft6/zenodo-metadata.md",
        "paper/draft6/architecture-sketch.svg",
    )
    for relative in required:
        if relative not in deliverables:
            fail(f"deliverable not listed: {relative}")
    acceptance = section_text(source, "acceptance")
    for ac in ("AC-01", "AC-02", "AC-03", "AC-06", "AC-08", "AC-09", "AC-10", "AC-15", "AC-16", "AC-21"):
        if ac not in acceptance:
            fail(f"acceptance criterion {ac} is missing")
    if not (root / "paper/draft5/README.md").is_file():
        fail("draft5 README is absent")
    for relative in ("docs/01-conceptual-model.md", "paper/draft5/README.md"):
        if not (root / relative).is_file():
            fail(f"alignment source is absent: {relative}")


def check_alignment(source: str, root: Path) -> None:
    # These are the exact two relative links used by the integrated evidence table.
    expected = {
        "../../01-conceptual-model.md": root / "docs/01-conceptual-model.md",
        "../../../paper/draft5/README.md": root / "paper/draft5/README.md",
    }
    for href, target in expected.items():
        if f'href="{href}"' not in source or not target.is_file():
            fail(f"draft5/docs alignment link is absent or broken: {href}")
    conceptual = (root / "docs/01-conceptual-model.md").read_text(encoding="utf-8").lower()
    for term in ("structured semantic state", "provenance", "revisit", "loop"):
        if term not in conceptual:
            fail(f"conceptual model no longer contains alignment term {term}")
    draft5_readme = (root / "paper/draft5/README.md").read_text(encoding="utf-8").lower()
    for term in ("paper source", "japanese companion", "references", "fact-check", "pdf builder", "static audit"):
        if term not in draft5_readme:
            fail(f"draft5 packaging evidence missing {term}")


def run_checks(path: Path, root: Path) -> list[CheckResult]:
    source, parser = parse_file(path)
    checks = (
        ("complete HTML parse", lambda: check_complete_html(path)),
        ("standalone resources and links", lambda: check_standalone(path)),
        ("architecture proposal attribute", lambda: check_architecture_attribute(parser)),
        ("accessible inline SVG", lambda: check_svg(source)),
        ("central thesis/phases/metrics/boundaries", lambda: check_content(source)),
        ("deliverables and acceptance", lambda: check_deliverables(source, root)),
        ("draft5/docs alignment", lambda: check_alignment(source, root)),
    )
    results: list[CheckResult] = []
    for name, check in checks:
        try:
            check()
        except VerificationError as exc:
            results.append(CheckResult(name, False, str(exc)))
        else:
            results.append(CheckResult(name, True, "ok"))
    return results


def print_results(results: list[CheckResult], prefix: str = "") -> None:
    for result in results:
        mark = "PASS" if result.ok else "FAIL"
        print(f"{prefix}{mark} {result.name}: {result.detail}")


def run_negative_tests(path: Path, root: Path) -> list[CheckResult]:
    mutations = {
        "remove architecture data attribute": (
            ' data-kamui-architecture-proposal="true"',
            "",
            "architecture proposal attribute",
        ),
        "remove central thesis term": (
            "表現形式（representation form）・精度（precision）・物理配置（physical placement）",
            "表現形式だけに置換した語",
            "central thesis/phases/metrics/boundaries",
        ),
        "remove required metric": (
            "HBM occupancy、相別byte数、metadata overhead",
            "相別byte数、metadata overhead",
            "central thesis/phases/metrics/boundaries",
        ),
        "remove draft5 alignment link": (
            'href="../../../paper/draft5/README.md"',
            'href="../../../paper/draft5/missing.md"',
            "draft5/docs alignment",
        ),
        "truncate HTML": ("</html>", "", "complete HTML parse"),
    }
    original = path.read_text(encoding="utf-8")
    results: list[CheckResult] = []
    with tempfile.TemporaryDirectory(prefix="requirements-verification-", dir=path.parent) as temp_dir:
        temp_root = Path(temp_dir)
        for name, (needle, replacement, expected_check) in mutations.items():
            if needle not in original:
                results.append(CheckResult(f"negative: {name}", False, "mutation needle absent"))
                continue
            mutated = original.replace(needle, replacement, 1)
            candidate = temp_root / f"{len(results)}.html"
            candidate.write_text(mutated, encoding="utf-8")
            candidate_results = run_checks(candidate, root)
            failed_names = {result.name for result in candidate_results if not result.ok}
            if expected_check not in failed_names:
                results.append(
                    CheckResult(
                        f"negative: {name}",
                        False,
                        f"expected {expected_check} to fail; failures={sorted(failed_names)}",
                    )
                )
            else:
                results.append(CheckResult(f"negative: {name}", True, f"{expected_check} failed as expected"))
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--negative", action="store_true", help="also run required-element removal tests")
    args = parser.parse_args(argv)
    root = Path.cwd()
    if not args.target.is_file():
        print(f"FAIL target does not exist: {args.target}", file=sys.stderr)
        return 2
    results = run_checks(args.target, root)
    print_results(results)
    if args.negative:
        negative = run_negative_tests(args.target, root)
        print_results(negative)
        results.extend(negative)
    failures = [result for result in results if not result.ok]
    print(f"SUMMARY: {len(results) - len(failures)} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
