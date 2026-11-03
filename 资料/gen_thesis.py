"""按《江西应用科技学院本科毕业设计（论文）撰写规范》生成毕业论文 Word 文档。
版式：A4，上2.8 下2.5 左2.5 右2.5cm，页眉1.6 页脚1.5cm，装订线0.5cm；正文小四宋体1.25倍行距；
章标题小三黑体，节标题四号黑体，条标题小四宋体；表题黑体五号居上，表内五号宋体，三线表；
参考文献标题四号黑体，内容小五宋体；页眉小五宋体居中带横线；页码从正文开始，底端居中。"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

import thesis_content as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "交付", "论文图片")
CITE = re.compile(r"(\[\d+(?:\]\[\d+)*\])")
SZ = {"小二": 18, "小三": 15, "四号": 14, "小四": 12, "五号": 10.5, "小五": 9}


def font(run, cn="宋体", size=12, bold=False, en="Times New Roman"):
    run.font.name = en
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    rf.set(qn("w:eastAsia"), cn)
    rf.set(qn("w:ascii"), en)
    rf.set(qn("w:hAnsi"), en)
    run.font.size = Pt(size)
    run.bold = bold


def pfmt(p, spacing=1.25, indent=None, before=0, after=0, align=None):
    f = p.paragraph_format
    f.line_spacing = spacing
    f.space_before = Pt(before)
    f.space_after = Pt(after)
    if indent is not None:
        f.first_line_indent = Pt(indent)
    if align is not None:
        p.alignment = align


def add_text(p, s, size=12, cn="宋体", bold=False):
    for part in CITE.split(s):
        if not part:
            continue
        r = p.add_run(part)
        font(r, cn, size, bold)
        if CITE.fullmatch(part):
            r.font.superscript = True


def heading(doc, s, level):
    p = doc.add_paragraph()
    if level == 1:
        pfmt(p, 1.25, before=12, after=12, align=WD_ALIGN_PARAGRAPH.CENTER)
        font(p.add_run(s), "黑体", SZ["小三"], True)
        p.style = doc.styles["Heading 1"]
    elif level == 2:
        pfmt(p, 1.25, before=6, after=6)
        font(p.add_run(s), "黑体", SZ["四号"], False)
        p.style = doc.styles["Heading 2"]
    else:
        pfmt(p, 1.25, before=3, after=3)
        font(p.add_run(s), "宋体", SZ["小四"], False)
        p.style = doc.styles["Heading 3"]
    for r in p.runs:
        r.font.color.rgb = None
    return p


def body(doc, s):
    p = doc.add_paragraph()
    pfmt(p, 1.25, indent=24)
    add_text(p, s)
    return p


def caption(doc, s, above=False):
    p = doc.add_paragraph()
    pfmt(p, 1.25, before=(6 if above else 0), after=(0 if above else 6), align=WD_ALIGN_PARAGRAPH.CENTER)
    font(p.add_run(s), "黑体", SZ["五号"])
    p.paragraph_format.keep_with_next = above


def border(cell, **kw):
    tcPr = cell._tc.get_or_add_tcPr()
    b = tcPr.find(qn("w:tcBorders"))
    if b is None:
        b = OxmlElement("w:tcBorders")
        tcPr.append(b)
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        sz = kw.get(edge)
        if sz:
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), str(sz))
            el.set(qn("w:color"), "000000")
        else:
            el.set(qn("w:val"), "nil")
        b.append(el)


def table(doc, title, header, rows):
    caption(doc, title, above=True)
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate([header] + rows):
        for j, val in enumerate(row):
            c = t.cell(i, j)
            c.text = ""
            p = c.paragraphs[0]
            pfmt(p, 1.0, align=WD_ALIGN_PARAGRAPH.CENTER if len(val) <= 14 else WD_ALIGN_PARAGRAPH.LEFT)
            font(p.add_run(val), "宋体", SZ["五号"], i == 0)
            top = 12 if i == 0 else (4 if i == 1 else None)
            bottom = 12 if i == len(rows) else None
            border(c, top=top, bottom=bottom)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def figure(doc, name, cap):
    path = os.path.join(FIG, name)
    if not os.path.exists(path):
        todo(doc, f"【缺图：请把截图保存为 交付/论文图片/{name} 后重新生成】")
        caption(doc, cap)
        return
    p = doc.add_paragraph()
    pfmt(p, 1.0, before=6, align=WD_ALIGN_PARAGRAPH.CENTER)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(path, width=Cm(15))
    caption(doc, cap)


def code(doc, s):
    for ln in s.split("\n"):
        p = doc.add_paragraph()
        pfmt(p, 1.0)
        p.paragraph_format.left_indent = Cm(0.75)
        font(p.add_run(ln or " "), "宋体", SZ["五号"], en="Consolas")


def todo(doc, s):
    p = doc.add_paragraph()
    pfmt(p, 1.25, before=6, after=6, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = p.add_run(s)
    font(r, "黑体", SZ["五号"])
    r.font.highlight_color = 7


def header_footer(section, text, page_numbers):
    section.header.is_linked_to_previous = False
    section.footer.is_linked_to_previous = False
    hp = section.header.paragraphs[0]
    hp.text = ""
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    font(hp.add_run(text), "宋体", SZ["小五"])
    pPr = hp._p.get_or_add_pPr()
    if not text:
        pPr = OxmlElement("w:pPr")
    bdr = OxmlElement("w:pBdr")
    bt = OxmlElement("w:bottom")
    for k, v in (("val", "single"), ("sz", "6"), ("space", "1"), ("color", "000000")):
        bt.set(qn(f"w:{k}"), v)
    bdr.append(bt)
    pPr.append(bdr)
    fp = section.footer.paragraphs[0]
    fp.text = ""
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if page_numbers:
        r = fp.add_run()
        font(r, "宋体", SZ["小五"])
        for tag, txt in (("begin", None), (None, "PAGE"), ("end", None)):
            if tag:
                el = OxmlElement("w:fldChar")
                el.set(qn("w:fldCharType"), tag)
            else:
                el = OxmlElement("w:instrText")
                el.set(qn("xml:space"), "preserve")
                el.text = txt
            r._r.append(el)


def page_setup(section):
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin, section.bottom_margin = Cm(2.8), Cm(2.5)
    section.left_margin, section.right_margin = Cm(2.5), Cm(2.5)
    section.header_distance, section.footer_distance = Cm(1.6), Cm(1.5)
    section.gutter = Cm(0.5)


COVER = [("学       院", "未来技术学院"), ("专       业", "智能科学与技术"), ("学       号", ""),
         ("学 生 姓 名", ""), ("指 导 教 师", "            职称")]


def blank(doc, n):
    for _ in range(n):
        pfmt(doc.add_paragraph(), 1.0)


def front_matter(doc, sec):
    """封面、诚信声明书、版权使用授权书，文字与格式取自《2027届本科毕业设计（论文）指导手册》本科毕业论文样式。"""
    header_footer(sec, "", False)
    blank(doc, 3)
    p = doc.add_paragraph()
    pfmt(p, 1.0, align=WD_ALIGN_PARAGRAPH.CENTER)
    font(p.add_run("本科毕业论文"), "宋体", 26, True)
    blank(doc, 4)
    p = doc.add_paragraph()
    pfmt(p, 1.0, align=WD_ALIGN_PARAGRAPH.CENTER)
    font(p.add_run(C.TITLE), "宋体", SZ["小二"], True)
    blank(doc, 4)
    for label, val in COVER:
        p = doc.add_paragraph()
        pfmt(p, 1.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        font(p.add_run(label + "    "), "宋体", 16, True)
        r = p.add_run(val.center(18, "\u3000") if val.strip() else "\u3000" * 9)
        font(r, "宋体", 16, True)
        r.underline = True
    blank(doc, 5)
    p = doc.add_paragraph()
    pfmt(p, 1.0, align=WD_ALIGN_PARAGRAPH.CENTER)
    font(p.add_run("二〇二七年    月"), "宋体", 16, True)

    s2 = doc.add_section(WD_SECTION.NEW_PAGE)
    header_footer(s2, "", False)
    blank(doc, 1)
    p = doc.add_paragraph()
    pfmt(p, 1.0, after=18, align=WD_ALIGN_PARAGRAPH.CENTER)
    font(p.add_run("江西应用科技学院毕业论文诚信声明书"), "黑体", SZ["小二"], True)
    for s in [f"本人郑重声明：本人所提交的毕业论文《{C.TITLE}》，是本人在指导教师的指导下取得的成果。毕业论文中所引用他人的无论以何种方式发布的文字、研究成果，均已加以说明；有关教师、同学和其他人员对本研究成果提出过并为我在毕业论文中加以采纳的意见、建议，均已在文中做了明确说明。",
              "如本人的毕业论文涉及抄袭或剽窃等行为，本人愿承担由此而造成的一切后果及责任。"]:
        p = doc.add_paragraph()
        pfmt(p, 1.5, indent=28)
        font(p.add_run(s), "宋体", 14)
    blank(doc, 1)
    p = doc.add_paragraph()
    pfmt(p, 1.5, indent=56)
    font(p.add_run("作者签名：                     日期："), "宋体", 14)
    blank(doc, 4)
    p = doc.add_paragraph()
    pfmt(p, 1.0, after=18, align=WD_ALIGN_PARAGRAPH.CENTER)
    font(p.add_run("毕业论文版权使用授权书"), "黑体", SZ["小二"], True)
    p = doc.add_paragraph()
    pfmt(p, 1.5, indent=28)
    font(p.add_run("本毕业论文作者完全了解学校有关保留、使用毕业论文的规定，同意学校保留并向国家有关部门或机构送交论文的复印件和电子版，允许论文被查阅和借阅。本人授权江西应用科技学院可以将本论文的全部或部分内容编入有关数据库进行检索，可以采用影印、缩印或扫描等复制手段保存和汇编本毕业论文。"), "宋体", 14)
    blank(doc, 1)
    for s in ("作者签名：                     日期：", "导师签名：                     日期："):
        p = doc.add_paragraph()
        pfmt(p, 1.5, indent=56)
        font(p.add_run(s), "宋体", 14)


def restart_numbering(section):
    sectPr = section._sectPr
    pg = OxmlElement("w:pgNumType")
    pg.set(qn("w:start"), "1")
    sectPr.append(pg)


def toc(doc):
    p = doc.add_paragraph()
    pfmt(p, 1.0, after=12, align=WD_ALIGN_PARAGRAPH.CENTER)
    font(p.add_run("目        录"), "黑体", SZ["小二"], True)
    p = doc.add_paragraph()
    r = p.add_run()
    for tag, txt in (("begin", None), (None, 'TOC \\o "1-2" \\h \\z \\u'), ("separate", None)):
        if tag:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), tag)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = txt
        r._r.append(el)
    r2 = p.add_run("（打开文档后右键此处选择“更新域”，或按 F9 生成目录）")
    font(r2, "宋体", SZ["小四"])
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    p.add_run()._r.append(end)


def count_body():
    n = 0
    for item in C.BODY:
        if item[0] in ("p", "h1", "h2", "h3"):
            n += len(re.sub(r"\s", "", CITE.sub("", item[1])))
    return n


def check_citations():
    order = []
    for item in C.BODY:
        if item[0] == "p":
            for m in re.finditer(r"\[(\d+)\]", item[1]):
                k = int(m.group(1))
                if k not in order:
                    order.append(k)
    assert order == list(range(1, len(order) + 1)), f"引用首次出现顺序不连续：{order}"
    assert len(order) == len(C.REFS), f"正文引用{len(order)}篇，参考文献表{len(C.REFS)}篇"
    return len(order)


def build(out):
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    st.font.size = Pt(12)
    for name in ("Heading 1", "Heading 2", "Heading 3"):
        hs = doc.styles[name]
        hs.font.color.rgb = None
        hs.element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")

    sec = doc.sections[0]
    page_setup(sec)
    front_matter(doc, sec)
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    header_footer(sec, "摘要", False)
    p = doc.add_paragraph()
    pfmt(p, 1.0, after=6, align=WD_ALIGN_PARAGRAPH.CENTER)
    font(p.add_run(C.TITLE), "宋体", SZ["小二"], True)
    p = doc.add_paragraph()
    pfmt(p, 1.0, after=12, align=WD_ALIGN_PARAGRAPH.CENTER)
    font(p.add_run("摘  要"), "黑体", SZ["小二"], True)
    for s in C.ABSTRACT:
        body(doc, s)
    p = doc.add_paragraph()
    pfmt(p, 1.25, before=12)
    font(p.add_run("关键词："), "黑体", SZ["小四"])
    font(p.add_run(C.KEYWORDS.replace("；", "； ")), "宋体", SZ["小四"])

    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    header_footer(sec, "ABSTRACT", False)
    p = doc.add_paragraph()
    pfmt(p, 1.0, after=6, align=WD_ALIGN_PARAGRAPH.CENTER)
    font(p.add_run(C.TITLE_EN), "宋体", SZ["小三"], True)
    p = doc.add_paragraph()
    pfmt(p, 1.0, after=12, align=WD_ALIGN_PARAGRAPH.CENTER)
    font(p.add_run("ABSTRACT"), "Times New Roman", SZ["小二"], True)
    for s in C.ABSTRACT_EN:
        p = doc.add_paragraph()
        pfmt(p, 1.25, indent=24, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        font(p.add_run(s), "Times New Roman", SZ["小四"])
    p = doc.add_paragraph()
    pfmt(p, 1.25, before=12)
    font(p.add_run("Key words: "), "Times New Roman", SZ["小四"], True)
    font(p.add_run(C.KEYWORDS_EN), "Times New Roman", SZ["小四"])

    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    header_footer(sec, "目录", False)
    toc(doc)

    first = True
    first_body_idx = None
    for item in C.BODY:
        kind = item[0]
        if kind == "h1":
            sec = doc.add_section(WD_SECTION.NEW_PAGE)
            name = item[1].replace("  ", " ")
            header_footer(sec, name if name != "结 论" else "结论", True)
            if first:
                restart_numbering(sec)
                first_body_idx = len(doc.sections) - 1
                first = False
            heading(doc, item[1], 1)
        elif kind == "h2":
            heading(doc, item[1], 2)
        elif kind == "h3":
            heading(doc, item[1], 3)
        elif kind == "p":
            body(doc, item[1])
        elif kind == "fig":
            figure(doc, item[1], item[2])
        elif kind == "table":
            table(doc, item[1], item[2], item[3])
        elif kind == "code":
            code(doc, item[1])
        elif kind == "todo":
            todo(doc, item[1])

    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    header_footer(sec, "参考文献", True)
    p = doc.add_paragraph()
    pfmt(p, 1.25, after=12, align=WD_ALIGN_PARAGRAPH.CENTER)
    font(p.add_run("参考文献"), "黑体", SZ["四号"], True)
    p.style = doc.styles["Heading 1"]
    for r in p.runs:
        r.font.color.rgb = None
        r.font.size = Pt(SZ["四号"])
    for i, ref in enumerate(C.REFS, 1):
        p = doc.add_paragraph()
        pfmt(p, 1.25)
        p.paragraph_format.left_indent = Pt(27)
        p.paragraph_format.first_line_indent = Pt(-27)
        en = not re.search(r"[\u4e00-\u9fff]", ref)
        font(p.add_run(f"[{i}]  {ref}"), "宋体", SZ["小五"], en="Times New Roman")

    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    header_footer(sec, "致谢", True)
    p = doc.add_paragraph()
    pfmt(p, 1.25, after=12, align=WD_ALIGN_PARAGRAPH.CENTER)
    font(p.add_run("致  谢"), "黑体", SZ["四号"], True)
    p.style = doc.styles["Heading 1"]
    for r in p.runs:
        r.font.color.rgb = None
        r.font.size = Pt(SZ["四号"])
    p = doc.add_paragraph()
    pfmt(p, 1.25, indent=21)
    font(p.add_run(C.THANKS), "宋体", SZ["五号"])

    for i, s in enumerate(doc.sections):
        page_setup(s)
        if i != first_body_idx:
            for el in s._sectPr.findall(qn("w:pgNumType")):
                s._sectPr.remove(el)
    doc.save(out)


if __name__ == "__main__":
    n_cite = check_citations()
    out = os.path.join(ROOT, "交付", "毕业论文_基于Coze智能体的法律咨询系统的设计与实现.docx")
    build(out)
    abs_n = len(re.sub(r"\s", "", C.ABSTRACT[0]))
    en_n = len(C.ABSTRACT_EN[0])
    foreign = sum(1 for r in C.REFS if not re.search(r"[\u4e00-\u9fff]", r))
    print(f"正文字数（不含图表）约 {count_body()}；中文摘要 {abs_n} 字；英文摘要 {en_n} 字符")
    print(f"参考文献 {len(C.REFS)} 篇（外文 {foreign} 篇），正文引用 {n_cite} 篇，首次引用顺序连续")
    print("已生成：", out)
