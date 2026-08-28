"""Build the English Paper 4 review PDF from its constrained LaTeX source."""

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
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


HERE = Path(__file__).resolve().parent
TEX = HERE / "topodialogue-en.tex"
BIB = HERE / "references.bib"
FIGURES = HERE.parent / "figures" / "draft4"


def bib_entries() -> tuple[list[str], dict[str, dict[str, str]]]:
    text = BIB.read_text(encoding="utf-8")
    order, entries = [], {}
    for match in re.finditer(r"@\w+\{([^,]+),(.*?)(?=\n\})\n", text, re.S):
        key, body = match.groups()
        order.append(key)
        entries[key] = {name.lower(): value.strip().replace("{", "").replace("}", "")
                        for name, value in re.findall(r"\b(\w+)\s*=\s*\{(.*?)\}\s*,?", body, re.S)}
    return order, entries


BIB_ORDER, BIB_ENTRIES = bib_entries()
BIB_NUMBER = {key: index + 1 for index, key in enumerate(BIB_ORDER)}


def inline(text: str) -> str:
    text = " ".join(text.split()).replace("---", "-").replace("--", "-").replace("~", " ")
    text = text.replace("それでいい", "sore de ii [Japanese]")
    text = text.replace("\\system", "TopoDialogue")
    text = re.sub(r"\\(?:code|texttt)\{([^{}]*)\}", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\\emph\{([^{}]*)\}", r"<i>\1</i>", text)
    def cite(match: re.Match[str]) -> str:
        return "[" + ", ".join(str(BIB_NUMBER[key.strip()]) for key in match.group(1).split(",")) + "]"
    text = re.sub(r"\\cite[pt]?\{([^{}]+)\}", cite, text)
    text = re.sub(r"\$([^$]+)\$", lambda m: html.escape(m.group(1).replace("\\quad", "  ").replace("\\", "")), text)
    text = text.replace("\\%", "%").replace("\\&", "&")
    text = text.replace("``", "\u201c").replace("''", "\u201d")
    return text


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=colors.HexColor("#17324d"), alignment=TA_CENTER, spaceAfter=5*mm),
        "author": ParagraphStyle("author", parent=base["Normal"], fontSize=10, leading=13, alignment=TA_CENTER, spaceAfter=7*mm),
        "abstract": ParagraphStyle("abstract", parent=base["BodyText"], fontName="Times-Roman", fontSize=8.8, leading=11.4, alignment=TA_JUSTIFY, leftIndent=8*mm, rightIndent=8*mm, spaceAfter=5*mm),
        "section": ParagraphStyle("section", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=13.5, leading=16, textColor=colors.HexColor("#17324d"), spaceBefore=5*mm, spaceAfter=2.5*mm, keepWithNext=True),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontName="Times-Roman", fontSize=9.2, leading=12, alignment=TA_JUSTIFY, spaceAfter=2.2*mm),
        "caption": ParagraphStyle("caption", parent=base["BodyText"], fontName="Helvetica", fontSize=7.6, leading=9.4, alignment=TA_CENTER, textColor=colors.HexColor("#3c4854"), spaceAfter=3*mm),
        "table": ParagraphStyle("table", parent=base["BodyText"], fontName="Helvetica", fontSize=7.3, leading=9),
        "reference": ParagraphStyle("reference", parent=base["BodyText"], fontName="Times-Roman", fontSize=7.7, leading=9.5, leftIndent=5*mm, firstLineIndent=-5*mm, spaceAfter=1.5*mm),
    }


def add_paragraphs(story: list, chunk: str, style: ParagraphStyle) -> None:
    chunk = re.sub(r"\\(?:centering|small|label\{[^{}]+\})", "", chunk)
    for paragraph in re.split(r"\n\s*\n", chunk):
        if paragraph.strip():
            story.append(Paragraph(inline(paragraph.strip()), style))


def table_from(block: str, style: dict[str, ParagraphStyle]) -> KeepTogether:
    content = re.search(r"\\begin\{tabular\}\{[^\n]*\}\s*(.*?)\\end\{tabular\}", block, re.S).group(1)
    rows = []
    for raw in content.split("\\\\"):
        raw = re.sub(r"\\(?:toprule|midrule|bottomrule)", "", raw).strip()
        if raw:
            rows.append([Paragraph(inline(cell.strip()), style["table"]) for cell in raw.split("&")])
    table = Table(rows, colWidths=[42*mm, 104*mm], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e8eef4")), ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#9aa8b5")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("PADDING", (0,0), (-1,-1), 4)]))
    caption = inline(re.search(r"\\caption\{(.*?)\}", block, re.S).group(1))
    return KeepTogether([Paragraph(caption, style["caption"]), table, Spacer(1, 3*mm)])


def figure_from(block: str, style: dict[str, ParagraphStyle]) -> KeepTogether:
    name = re.search(r"\\includegraphics(?:\[[^]]*\])?\{([^{}]+)\}", block).group(1)
    image = Image(str(FIGURES / name))
    scale = min(154*mm/image.imageWidth, 88*mm/image.imageHeight)
    image.drawWidth, image.drawHeight = image.imageWidth*scale, image.imageHeight*scale
    caption = inline(re.search(r"\\caption\{(.*?)\}", block, re.S).group(1))
    return KeepTogether([image, Spacer(1, 1.5*mm), Paragraph(caption, style["caption"])])


def reference(number: int, fields: dict[str, str], style: ParagraphStyle) -> Paragraph:
    author = fields.get("author", "").replace(" and ", "; ")
    venue = fields.get("journal") or fields.get("booktitle") or fields.get("institution") or fields.get("publisher", "")
    link = f"https://doi.org/{fields['doi']}" if fields.get("doi") else fields.get("url", "")
    rendered = f"[{number}] {author} ({fields.get('year','')}). <i>{fields.get('title','')}</i>. {venue}"
    if link:
        rendered += f". <link href='{html.escape(link, quote=True)}' color='#1f4e79'>{html.escape(link)}</link>"
    return Paragraph(rendered, style)


def footer(canvas, document) -> None:
    canvas.saveState(); canvas.setStrokeColor(colors.HexColor("#ccd5dd")); canvas.line(25*mm, 16*mm, A4[0]-25*mm, 16*mm)
    canvas.setFont("Helvetica", 7.5); canvas.setFillColor(colors.HexColor("#66717c")); canvas.drawString(25*mm, 11*mm, "TopoDialogue IV - review PDF"); canvas.drawRightString(A4[0]-25*mm, 11*mm, str(document.page)); canvas.restoreState()


def build(output: Path) -> None:
    text, style, story = TEX.read_text(encoding="utf-8"), styles(), []
    abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", text, re.S).group(1)
    story.extend([Paragraph("TopoDialogue IV: What Transcription Leaves Behind<br/>Modality-Preserving Events for Accessible Human-AI Dialogue", style["title"]), Paragraph("Ryoko Sakakibara - Independent Researcher<br/>16 August 2026", style["author"]), Paragraph("<b>Abstract</b>", style["body"]), Paragraph(inline(abstract), style["abstract"])])
    body = re.search(r"\\end\{abstract\}(.*?)\\bibliographystyle", text, re.S).group(1)
    token = re.compile(r"(\\begin\{(?:table|figure|equation)\}.*?\\end\{(?:table|figure|equation)\}|\\section\{[^{}]+\})", re.S)
    position = 0
    for match in token.finditer(body):
        add_paragraphs(story, body[position:match.start()], style["body"]); block = match.group(0)
        if block.startswith("\\section"):
            story.append(Paragraph(inline(re.search(r"\{([^{}]+)\}", block).group(1)), style["section"]))
        elif "{table}" in block:
            story.append(table_from(block, style))
        elif "{figure}" in block:
            story.append(figure_from(block, style))
        else:
            equation = re.search(r"\\begin\{equation\}(.*?)\\end\{equation\}", block, re.S).group(1)
            story.append(Paragraph(inline(equation), style["body"]))
        position = match.end()
    add_paragraphs(story, body[position:], style["body"])
    story.append(Paragraph("References", style["section"]))
    story.extend(reference(i, BIB_ENTRIES[key], style["reference"]) for i, key in enumerate(BIB_ORDER, 1))
    output.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=25*mm, leftMargin=25*mm, topMargin=21*mm, bottomMargin=21*mm, title="TopoDialogue IV: What Transcription Leaves Behind", author="Ryoko Sakakibara")
    document.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "topodialogue-draft4-en.pdf"
    build(target.resolve()); print(target.resolve())
