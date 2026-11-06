"""填写《智科2027届毕业设计附件材料模板》中学生应填部分：封面、任务书、文献综述、开题报告前6项、中期检查表学生部分、各表题目。
姓名、学号、指导教师、职称、日期、签名留空，由作者本人填写；指导教师、评阅教师、答辩组填写的内容不动。"""
import copy
import os
import re
import sys
import docx
from docx.oxml import OxmlElement
from docx.table import Table

sys.path.insert(0, os.path.dirname(__file__))
import gen_review as R
import gen_proposal as P
from fill_handbook import (TITLE, W, runs, rtext, set_rtext, ptext, drop_red, fill_blank, rpr_of, clean_rpr,
                           add_runs, new_par, set_line_spacing, has_break, find, unique_cells, set_cell, fill_task)

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "智科2027届毕业设计附件材料模板.docx")
OUT = os.path.join(HERE, "..", "交付", "附件材料_基于Coze智能体的法律咨询系统的设计与实现.docx")

PROGRESS = ("已完成文献综述和开题报告。在扣子平台搭建并发布了法律咨询智能体，从国家法律法规数据库整理6部现行法律共1706条条文作为知识库；"
            "完成Spring Boot后端和Vue3前端开发并接入智能体，实现了智能咨询、咨询记录、法条查询、律师预约和后台管理等功能；"
            "完成功能测试（28项全部通过）、性能测试和智能体问答效果测试（挂载知识库的智能体法律依据正确43/50，对照组39/50）；"
            "论文初稿已完成，正在根据指导教师意见修改。")
KEY = "以现行法律条文为知识库约束智能体的答复依据，减少法律幻觉；后端以流式方式接入扣子智能体并管理多轮会话；通过对照实验检验知识库的作用。"


def blank_placeholder(p, words):
    """把“居  中”“可删除”等占位提示换成等宽空格，保留下划线。"""
    for r in runs(p):
        t = rtext(r)
        for w in words:
            if w in t:
                t = t.replace(w, " " * (len(w) * 2 if not w.isascii() else len(w)))
        set_rtext(r, t)


def set_title_line(p, label):
    """封面题目行：标签 + 题目（下划线），去掉格式说明，左对齐，第二行用下划线空格补满。"""
    rs = runs(p)
    set_rtext(rs[0], label)
    u = next(r for r in rs[1:] if r.find(W("w:rPr") + "/" + W("w:u")) is not None)
    set_rtext(u, " " + TITLE + " " * 26)
    for r in rs[1:]:
        if r is not u:
            p.remove(r)
    ppr = p.find(W("w:pPr"))
    for el in ppr.findall(W("w:ind")) + ppr.findall(W("w:jc")):
        ppr.remove(el)
    jc = OxmlElement("w:jc")
    jc.set(W("w:val"), "left")
    ppr.append(jc)


def remove(el):
    el.getparent().remove(el)


def fill_title_cell(table, ri, ci=1):
    cell = unique_cells(table.rows[ri])[ci]
    lab = rpr_of(unique_cells(table.rows[ri])[0].paragraphs[0]._p)
    set_cell(cell, TITLE, lab)


def build():
    d = docx.Document(SRC)
    body = list(d.element.body.iterchildren())

    # 附件材料封面
    i = find(body, 0, lambda t: t.startswith("毕业设计题目"))
    set_title_line(body[i], "毕业设计题目")
    remove(body[i + 1])
    body = list(d.element.body.iterchildren())
    j = find(body, i, lambda t: "——XXXXXXXX" in t)
    remove(body[j])
    body = list(d.element.body.iterchildren())
    j = find(body, i, lambda t: t.startswith("学       院"))
    for r in runs(body[j]):
        if "三号宋体" in rtext(r):
            body[j].remove(r)
    j = find(body, j, lambda t: t.startswith("指 导 教 师"))
    blank_placeholder(body[j], ["居  中"])
    blank_placeholder(body[j + 1], ["无第二导师删除", "可删除"])

    # 任务书封面与正文
    i = find(body, j, lambda t: t.strip() == "本科毕业设计任务书")
    i = find(body, i, lambda t: t.startswith("设计题目"))
    set_title_line(body[i], "设计题目 ")
    remove(body[i + 1])
    body = list(d.element.body.iterchildren())
    for k in range(i, i + 4):
        blank_placeholder(body[k], ["居  中"])
    k = find(body, i, lambda t: t.replace(" ", "") == "任务书")
    tbl = next(el for el in body[k:] if el.tag == W("w:tbl"))
    fill_task(Table(tbl, d))

    # 文献综述
    i = find(body, k, lambda t: t.strip() == "本科毕业设计文献综述")
    i = find(body, i, lambda t: t.strip().startswith("设计题目"))
    fill_blank(body[i], TITLE)
    h0 = find(body, i, lambda t: t.startswith("一、引言"))
    h1 = find(body, h0, lambda t: t.startswith("二、研究意义"))
    end = next(n for n in range(h1, len(body)) if body[n].tag == W("w:p") and has_break(body[n]))
    head_t, body_t = copy.deepcopy(body[h1]), copy.deepcopy(body[h1 + 1])
    anchor = body[end]
    for el in body[h0:end]:
        remove(el)
    for h, ps in R.SECTIONS:
        anchor.addprevious(new_par(head_t, h, bold=True, indent=False, cite=False))
        for t in ps:
            if t.startswith("（") and len(t) < 30:
                anchor.addprevious(new_par(body_t, t, bold=True))
            else:
                anchor.addprevious(new_par(body_t, t))
    anchor.addprevious(new_par(head_t, "七、参考文献", bold=True, indent=False, cite=False))
    for n, ref in enumerate(R.REFS, 1):
        anchor.addprevious(new_par(body_t, f"[{n}] {ref}", size=21, hanging=525, cite=False))

    # 开题报告
    body = list(d.element.body.iterchildren())
    i = find(body, body.index(anchor), lambda t: t.strip() == "本科毕业设计开题报告")
    i = find(body, i, lambda t: t.strip().startswith("设计题目"))
    fill_blank(body[i], TITLE)
    k = find(body, i, lambda t: t.replace(" ", "") == "开题报告")
    tbl = next(el for el in body[k:] if el.tag == W("w:tbl"))
    table = Table(tbl, d)
    contents = [ps for _, ps in P.SECTIONS] + [[f"[{n}] {ref}" for n, ref in enumerate(P.REFS, 1)]]
    for row, ps in zip(table.rows, contents):
        cell = unique_cells(row)[0]
        paras = [x._p for x in cell.paragraphs]
        head = paras[0]
        for x in paras[1:]:
            remove(x)
        for r in runs(head)[1:]:
            if rtext(r).startswith("[1]"):
                head.remove(r)
        tmpl = copy.deepcopy(head)
        last = head
        for t in ps:
            if re.match(r"^\[\d+\] ", t):
                np_ = new_par(tmpl, t, size=21, hanging=525, cite=False)
            elif re.match(r"^（\d）", t):
                np_ = new_par(tmpl, t, bold=True, size=24, indent=False)
            else:
                np_ = new_par(tmpl, t, size=24)
            set_line_spacing(np_)
            last.addnext(np_)
            last = np_

    # 班级：2027届为2023级
    for p in d.element.body.iter(W("w:p")):
        for r in runs(p):
            if "2022级智能科学与技术" in rtext(r):
                set_rtext(r, rtext(r).replace("2022级", "2023级"))
            elif rtext(r) == "2022" and "学院" in ptext(p) and "级" in ptext(p):
                set_rtext(r, "2023")

    # 各表题目（第二次答辩相关表格仅在需要时填写，不预填）
    t = d.tables
    fill_title_cell(t[2], 3)
    fill_title_cell(t[3], 3)
    for n in (4, 5, 6, 7):
        fill_title_cell(t[n], 0)
    fill_title_cell(t[8], 3)
    fill_title_cell(t[9], 1)
    fill_title_cell(t[10], 1)

    # 中期检查表学生部分
    t3 = t[3]
    lab = rpr_of(unique_cells(t3.rows[0])[0].paragraphs[0]._p)
    c = unique_cells(t3.rows[4])
    set_cell(c[1], "否", lab)
    set_cell(c[3], "无", lab)
    c = unique_cells(t3.rows[5])
    for k in (1, 3, 5):
        set_cell(c[k], "是", lab)
    c = unique_cells(t3.rows[6])
    set_cell(c[1], KEY, lab)
    set_cell(c[3], "2027年4月", lab)
    paras = [x._p for x in unique_cells(t3.rows[7])[0].paragraphs]
    tgt = paras[1] if len(paras) > 1 else paras[0]
    for r in runs(tgt):
        tgt.remove(r)
    add_runs(tgt, PROGRESS, clean_rpr(copy.deepcopy(lab)), cite=False)

    # 成绩评定书题目
    body = list(d.element.body.iterchildren())
    i = find(body, 0, lambda t: t.startswith("毕业设计题目："))
    u = next(r for r in runs(body[i]) if r.find(W("w:rPr") + "/" + W("w:u")) is not None)
    set_rtext(u, TITLE)

    d.save(OUT)
    print("saved", os.path.abspath(OUT))


if __name__ == "__main__":
    build()
