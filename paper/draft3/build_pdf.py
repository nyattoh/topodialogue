"""Build the English Draft 3 PDF without requiring a TeX installation.

The canonical submission source remains ``topodialogue-en.tex``.  This small
renderer understands the deliberately limited LaTeX subset used by that file
and produces a readable A4 review PDF with ReportLab.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

HERE = Path(__file__).resolve().parent
TEX = HERE / "topodialogue-en.tex"
BIB = HERE / "references.bib"
FIGURES = HERE.parent / "figures" / "draft3"


def bib_entries() -> tuple[list[str], dict[str, dict[str, str]]]:
    text = BIB.read_text(encoding="utf-8")
    order: list[str] = []
    entries: dict[str, dict[str, str]] = {}
    for match in re.finditer(r"@\w+\{([^,]+),(.*?)(?=\n\})\n", text, re.S):
        key, body = match.groups()
        order.append(key)
        fields = {
            name.lower(): value.strip().replace("{", "").replace("}", "")
            for name, value in re.findall(r"\b(\w+)\s*=\s*\{(.*?)\}\s*,?", body, re.S)
        }
        entries[key] = fields
    return order, entries


BIB_ORDER, BIB_ENTRIES = bib_entries()
BIB_NUMBER = {key: index + 1 for index, key in enumerate(BIB_ORDER)}
REFS = {"tab:events": "1", "tab:counts": "2", "tab:comparison": "3",
        "fig:counts": "1", "fig:comparison": "2", "fig:trajectory": "3"}


def inline(text: str) -> str:
    text = " ".join(text.split())
    text = text.replace("---", "—").replace("--", "–").replace("~", " ")
    text = text.replace("\\system{}", "TopoDialogue")
    text = re.sub(r"\\code\{([^{}]*)\}", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\\emph\{([^{}]*)\}", r"<i>\1</i>", text)
    text = re.sub(r"\\textsc\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\texttt\{([^{}]*)\}", r"<font name='Courier'>\1</font>", text)

    def cite(match: re.Match[str]) -> str:
        nums = [str(BIB_NUMBER[key.strip()]) for key in match.group(1).split(",")]
        return "[" + ", ".join(nums) + "]"

    text = re.sub(r"\\citep\{([^{}]+)\}", cite, text)
    text = re.sub(r"\\ref\{([^{}]+)\}", lambda m: REFS.get(m.group(1), "?"), text)
    text = re.sub(
        r"\\url\{([^{}]+)\}",
        lambda m: f"<link href='{html.escape(m.group(1), quote=True)}' color='#1f4e79'>{html.escape(m.group(1))}</link>",
        text,
    )
    text = text.replace("$D=(u_1,\\ldots,u_T)$", "D = (u1, …, uT)")
    text = re.sub(r"\$([^$]+)\$", lambda m: html.escape(m.group(1).replace("\\geq", "≥").replace("\\in", "∈")), text)
    text = text.replace("\\%", "%").replace("\\&", "&")
    text = text.replace("``", "“").replace("''", "”")
    return text


def caption_from(block: str) -> str:
    match = re.search(r"\\caption\{(.*?)\}\s*\\label", block, re.S)
    if not match:
        match = re.search(r"\\caption\{(.*?)\}", block, re.S)
    return inline(match.group(1)) if match else ""


def table_from(block: str, styles: dict[str, ParagraphStyle]) -> KeepTogether:
    # Column declarations may themselves contain braces (for example p{21mm}),
    # so consume the complete declaration line rather than stopping early.
    tabular = re.search(r"\\begin\{tabular\}\{[^\n]*\}\s*(.*?)\\end\{tabular\}", block, re.S)
    rows: list[list[Paragraph]] = []
    if tabular:
        for raw in tabular.group(1).split("\\\\"):
            raw = re.sub(r"\\(?:toprule|midrule|bottomrule)", "", raw).strip()
            if not raw:
                continue
            cells = [Paragraph(inline(cell.strip()), styles["table"]) for cell in raw.split("&")]
            rows.append(cells)
    widths = [34 * mm, 121 * mm] if rows and len(rows[0]) == 2 and len(rows) > 5 else None
    table = Table(rows, colWidths=widths, repeatRows=1, hAlign="CENTER")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#17324d")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#9aa8b5")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return KeepTogether([Paragraph(caption_from(block), styles["caption"]), Spacer(1, 2 * mm), table, Spacer(1, 3 * mm)])


def figure_from(block: str, styles: dict[str, ParagraphStyle]) -> KeepTogether:
    name = re.search(r"\\includegraphics(?:\[[^]]*\])?\{([^{}]+)\}", block).group(1)
    image = Image(str(FIGURES / name))
    max_w, max_h = 155 * mm, 92 * mm
    scale = min(max_w / image.imageWidth, max_h / image.imageHeight)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    return KeepTogether([image, Spacer(1, 1.5 * mm), Paragraph(caption_from(block), styles["caption"]), Spacer(1, 4 * mm)])


def reference_paragraph(number: int, fields: dict[str, str], style: ParagraphStyle) -> Paragraph:
    author = fields.get("author", "").replace(" and ", "; ")
    title = fields.get("title", "")
    venue = fields.get("journal") or fields.get("booktitle") or fields.get("publisher", "")
    details = ", ".join(value for value in [fields.get("volume"), fields.get("number"), fields.get("pages")] if value)
    tail = fields.get("doi") or fields.get("url", "")
    link = f"https://doi.org/{tail}" if fields.get("doi") else tail
    rendered = f"[{number}] {author} ({fields.get('year', '')}). <i>{title}</i>. {venue}"
    if details:
        rendered += f", {details}"
    if link:
        rendered += f". <link href='{html.escape(link, quote=True)}' color='#1f4e79'>{html.escape(link)}</link>"
    return Paragraph(rendered, style)


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("PaperTitle", parent=base["Title"], fontName="Helvetica-Bold", fontSize=19, leading=23, textColor=colors.HexColor("#17324d"), alignment=TA_CENTER, spaceAfter=6 * mm),
        "author": ParagraphStyle("Author", parent=base["Normal"], fontSize=10.5, leading=14, alignment=TA_CENTER, spaceAfter=8 * mm),
        "abstract_head": ParagraphStyle("AbstractHead", parent=base["Heading2"], fontSize=11, leading=14, textColor=colors.HexColor("#17324d"), spaceAfter=2 * mm),
        "abstract": ParagraphStyle("Abstract", parent=base["BodyText"], fontSize=9, leading=12, alignment=TA_JUSTIFY, leftIndent=9 * mm, rightIndent=9 * mm, spaceAfter=6 * mm),
        "section": ParagraphStyle("Section", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=14, leading=17, textColor=colors.HexColor("#17324d"), spaceBefore=7 * mm, spaceAfter=3 * mm, keepWithNext=True),
        "subsection": ParagraphStyle("Subsection", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=11.5, leading=14, textColor=colors.HexColor("#315a7d"), spaceBefore=4 * mm, spaceAfter=2 * mm, keepWithNext=True),
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontName="Times-Roman", fontSize=9.4, leading=12.2, alignment=TA_JUSTIFY, spaceAfter=2.4 * mm),
        "small": ParagraphStyle("Small", parent=base["BodyText"], fontName="Times-Roman", fontSize=8.2, leading=10.5, spaceAfter=1.8 * mm),
        "caption": ParagraphStyle("Caption", parent=base["BodyText"], fontName="Helvetica", fontSize=7.7, leading=9.6, alignment=TA_CENTER, textColor=colors.HexColor("#3c4854"), spaceAfter=2 * mm),
        "table": ParagraphStyle("Table", parent=base["BodyText"], fontName="Helvetica", fontSize=7.3, leading=9.2),
        "equation": ParagraphStyle("Equation", parent=base["BodyText"], fontName="Times-Italic", fontSize=10.5, leading=14, alignment=TA_CENTER, spaceBefore=2 * mm, spaceAfter=3 * mm),
        "reference": ParagraphStyle("Reference", parent=base["BodyText"], fontName="Times-Roman", fontSize=7.8, leading=9.8, leftIndent=5 * mm, firstLineIndent=-5 * mm, spaceAfter=1.8 * mm),
    }


def parse_story(story: list, text: str, style: dict[str, ParagraphStyle]) -> None:
    body = re.search(r"\\begin\{document\}(.*?)\\bibliographystyle", text, re.S).group(1)
    body = re.sub(r"\\maketitle", "", body)
    abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", body, re.S)
    story.extend([
        Paragraph("TopoDialogue III: Beyond the Transcript—Observable Implicit<br/>Interactional Structure in Human–AI Dialogue", style["title"]),
        Paragraph("Ryoko Sakakibara · Independent Researcher<br/>16 August 2026", style["author"]),
        Paragraph("Abstract", style["abstract_head"]),
        Paragraph(inline(abstract.group(1)), style["abstract"]),
    ])
    body = body[:abstract.start()] + body[abstract.end():]
    token = re.compile(
        r"(\\begin\{(?:table|figure\*?|enumerate|equation)\}.*?\\end\{(?:table|figure\*?|enumerate|equation)\}|"
        r"\\section\*?\{[^{}]+\}|\\subsection\{[^{}]+\}|\\paragraph\{[^{}]+\})",
        re.S,
    )
    position = 0
    for match in token.finditer(body):
        add_paragraphs(story, body[position:match.start()], style["body"])
        block = match.group(0)
        if block.startswith("\\section"):
            story.append(Paragraph(inline(re.search(r"\{([^{}]+)\}", block).group(1)), style["section"]))
        elif block.startswith("\\subsection"):
            story.append(Paragraph(inline(re.search(r"\{([^{}]+)\}", block).group(1)), style["subsection"]))
        elif block.startswith("\\paragraph"):
            heading = re.search(r"\{([^{}]+)\}", block).group(1)
            story.append(Paragraph(f"<b>{inline(heading)}.</b>", style["body"]))
        elif "{table}" in block:
            story.append(table_from(block, style))
        elif "{figure" in block:
            story.append(figure_from(block, style))
        elif "{enumerate}" in block:
            items = [Paragraph(inline(item), style["body"]) for item in re.findall(r"\\item\s+(.*?)(?=\\item|\\end\{enumerate\})", block, re.S)]
            story.append(ListFlowable([ListItem(item) for item in items], bulletType="1", leftIndent=8 * mm))
            story.append(Spacer(1, 2 * mm))
        elif "{equation}" in block:
            equation = re.search(r"\\begin\{equation\}(.*?)\\end\{equation\}", block, re.S).group(1)
            equation = equation.replace("\\frac{|F_t\\cap F_j|}{|F_t\\cup F_j|}", "|Ft ∩ Fj| / |Ft ∪ Fj|")
            story.append(Paragraph(inline(equation), style["equation"]))
        position = match.end()
    add_paragraphs(story, body[position:], style["body"])


def add_paragraphs(story: list, chunk: str, style: ParagraphStyle) -> None:
    chunk = re.sub(r"\\(?:centering|small|label\{[^{}]+\})", "", chunk)
    for paragraph in re.split(r"\n\s*\n", chunk):
        paragraph = paragraph.strip()
        if paragraph:
            story.append(Paragraph(inline(paragraph), style))


def footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#ccd5dd"))
    canvas.line(25 * mm, 16 * mm, A4[0] - 25 * mm, 16 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#66717c"))
    canvas.drawString(25 * mm, 11 * mm, "TopoDialogue III · review PDF")
    canvas.drawRightString(A4[0] - 25 * mm, 11 * mm, str(document.page))
    canvas.restoreState()


def build(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    style = styles()
    story: list = []
    parse_story(story, TEX.read_text(encoding="utf-8"), style)
    story.extend([PageBreak(), Paragraph("References", style["section"])])
    story.extend(reference_paragraph(i, BIB_ENTRIES[key], style["reference"]) for i, key in enumerate(BIB_ORDER, 1))
    document = SimpleDocTemplate(
        str(output), pagesize=A4, rightMargin=25 * mm, leftMargin=25 * mm,
        topMargin=22 * mm, bottomMargin=21 * mm,
        title="TopoDialogue III: Beyond the Transcript",
        author="Ryoko Sakakibara",
        subject="Observable implicit interactional structure in human–AI dialogue",
    )
    document.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "topodialogue-draft3-en.pdf"
    build(target.resolve())
    print(target.resolve())
