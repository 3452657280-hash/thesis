"""把带 [n] 引用标记的纯文本生成为 Word 文档：引用转为上标，正文宋体小四、1.5 倍行距。"""
import re
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt, Cm

CITE = re.compile(r"(\[\d+(?:[,，\-–]\d+)*\])")


def _font(run, name="宋体", size=12, bold=False):
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold


def new_doc():
    doc = Document()
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Cm(2.5)
        s.left_margin = s.right_margin = Cm(2.5)
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    st.font.size = Pt(12)
    return doc


def title(doc, text, size=16):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _font(p.add_run(text), "黑体", size, True)
    return p


def heading(doc, text, size=14):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.line_spacing = 1.5
    _font(p.add_run(text), "黑体", size, True)
    return p


def para(doc, text, indent=True, size=12):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing = 1.5
    if indent:
        pf.first_line_indent = Pt(size * 2)
    for part in CITE.split(text):
        if not part:
            continue
        r = p.add_run(part)
        _font(r, size=size)
        if CITE.fullmatch(part):
            r.font.superscript = True
    return p


def refs(doc, items, size=10.5):
    for i, it in enumerate(items, 1):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.line_spacing = 1.25
        pf.left_indent = Pt(size * 2.5)
        pf.first_line_indent = Pt(-size * 2.5)
        _font(p.add_run(f"[{i}]  {it}"), size=size)


def count_cn(texts):
    return sum(len(re.sub(r"\s", "", CITE.sub("", t))) for t in texts)
