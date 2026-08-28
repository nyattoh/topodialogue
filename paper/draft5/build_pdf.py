"""Build a polished review PDF from the constrained Paper 5 LaTeX source."""
from __future__ import annotations
import html, re, sys
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; TEX=HERE/"topodialogue-en.tex"; BIB=HERE/"references.bib"; FIGURES=ROOT/"paper"/"figures"/"draft5"

def bib_entries():
    text=BIB.read_text(encoding="utf-8"); order=[]; entries={}
    for match in re.finditer(r"@\w+\{([^,]+),(.*?)(?=\n\})\n",text,re.S):
        key,body=match.groups(); order.append(key); entries[key]={n.lower():v.strip().replace("{","").replace("}","") for n,v in re.findall(r"\b(\w+)\s*=\s*\{(.*?)\}\s*,?",body,re.S)}
    return order,entries

ORDER,ENTRIES=bib_entries(); NUMBER={key:i+1 for i,key in enumerate(ORDER)}
def inline(text):
    text=" ".join(text.split()).replace("---","-").replace("--","-").replace("~"," ")
    text=re.sub(r"\\(?:emph|texttt)\{([^{}]*)\}",r"<i>\1</i>",text)
    text=re.sub(r"\\cite[pt]?\{([^{}]+)\}",lambda m:"["+", ".join(str(NUMBER[k.strip()]) for k in m.group(1).split(","))+"]",text)
    return text.replace("\\%","%").replace("\\&","&")

def styles():
    b=getSampleStyleSheet(); return {
      "title":ParagraphStyle("t",parent=b["Title"],fontName="Helvetica-Bold",fontSize=18,leading=22,textColor=colors.HexColor("#17324d"),alignment=TA_CENTER,spaceAfter=5*mm),
      "author":ParagraphStyle("a",parent=b["Normal"],fontSize=10,leading=13,alignment=TA_CENTER,spaceAfter=6*mm),
      "abstract":ParagraphStyle("ab",parent=b["BodyText"],fontName="Times-Roman",fontSize=8.8,leading=11.4,alignment=TA_JUSTIFY,leftIndent=8*mm,rightIndent=8*mm,spaceAfter=4*mm),
      "section":ParagraphStyle("s",parent=b["Heading1"],fontName="Helvetica-Bold",fontSize=13,leading=16,textColor=colors.HexColor("#17324d"),spaceBefore=4*mm,spaceAfter=2*mm,keepWithNext=True),
      "body":ParagraphStyle("b",parent=b["BodyText"],fontName="Times-Roman",fontSize=9.2,leading=12,alignment=TA_JUSTIFY,spaceAfter=2.2*mm),
      "caption":ParagraphStyle("c",parent=b["BodyText"],fontName="Helvetica",fontSize=7.5,leading=9,alignment=TA_CENTER,textColor=colors.HexColor("#4d5965"),spaceAfter=3*mm),
      "ref":ParagraphStyle("r",parent=b["BodyText"],fontName="Times-Roman",fontSize=7.6,leading=9.3,leftIndent=5*mm,firstLineIndent=-5*mm,spaceAfter=1.3*mm)}

def add_text(story,chunk,style):
    chunk=re.sub(r"\\(?:centering|label\{[^{}]+\})","",chunk)
    for p in re.split(r"\n\s*\n",chunk):
        if p.strip(): story.append(Paragraph(inline(p.strip()),style))

def footer(canvas,doc):
    canvas.saveState(); canvas.setStrokeColor(colors.HexColor("#ccd5dd")); canvas.line(25*mm,16*mm,A4[0]-25*mm,16*mm); canvas.setFont("Helvetica",7.5); canvas.setFillColor(colors.HexColor("#66717c")); canvas.drawString(25*mm,11*mm,"TopoDialogue V - review PDF"); canvas.drawRightString(A4[0]-25*mm,11*mm,str(doc.page)); canvas.restoreState()

def build(output):
    text=TEX.read_text(encoding="utf-8"); st=styles(); story=[Paragraph("TopoDialogue V: Agency, Rendering Sovereignty,<br/>and Intervention on Dialogue Trajectories",st["title"]),Paragraph("Ryoko Sakakibara - Independent Researcher<br/>16 August 2026",st["author"])]
    abstract=re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}",text,re.S).group(1); story.extend([Paragraph("<b>Abstract</b>",st["body"]),Paragraph(inline(abstract),st["abstract"])])
    body=re.search(r"\\end\{abstract\}(.*?)\\bibliographystyle",text,re.S).group(1); token=re.compile(r"(\\section\{[^{}]+\}|\\begin\{figure\}.*?\\end\{figure\})",re.S); pos=0
    for m in token.finditer(body):
        add_text(story,body[pos:m.start()],st["body"]); block=m.group(0)
        if block.startswith("\\section"):
            story.append(Paragraph(re.search(r"\{([^{}]+)\}",block).group(1),st["section"]))
        else:
            name=re.search(r"\\includegraphics(?:\[[^]]*\])?\{([^{}]+)\}",block).group(1); image=Image(str(FIGURES/name)); scale=min(154*mm/image.imageWidth,82*mm/image.imageHeight); image.drawWidth=image.imageWidth*scale; image.drawHeight=image.imageHeight*scale; caption=inline(re.search(r"\\caption\{(.*?)\}",block,re.S).group(1)); story.append(KeepTogether([image,Spacer(1,1*mm),Paragraph(caption,st["caption"])]))
        pos=m.end()
    add_text(story,body[pos:],st["body"]); story.append(Paragraph("References",st["section"]))
    for i,key in enumerate(ORDER,1):
        f=ENTRIES[key]; venue=f.get("journal") or f.get("booktitle") or f.get("publisher",""); link=f"https://doi.org/{f['doi']}"; story.append(Paragraph(f"[{i}] {f.get('author','').replace(' and ','; ')} ({f.get('year','')}). <i>{f.get('title','')}</i>. {venue}. <link href='{link}' color='#1f4e79'>{link}</link>",st["ref"]))
    output.parent.mkdir(parents=True,exist_ok=True); doc=SimpleDocTemplate(str(output),pagesize=A4,rightMargin=25*mm,leftMargin=25*mm,topMargin=21*mm,bottomMargin=21*mm,title="TopoDialogue V: Agency, Rendering Sovereignty, and Intervention on Dialogue Trajectories",author="Ryoko Sakakibara"); doc.build(story,onFirstPage=footer,onLaterPages=footer)

if __name__ == "__main__":
    target=Path(sys.argv[1]) if len(sys.argv)>1 else HERE/"topodialogue-draft5-en.pdf"; build(target.resolve()); print(target.resolve())
