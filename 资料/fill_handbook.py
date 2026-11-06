"""在指导手册（docx 副本）中填写学生应填部分：附件3 封面、附件4 任务书（封面与正文，指导教师签名留空）、附件5 文献综述、附件6 开题报告前6项、附件8 中期检查表学生部分。
姓名、学号、班级、指导教师、职称、日期留空，由作者本人填写。"""
import copy
import os
import re
import sys
import docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.table import Table
from docx.text.paragraph import Paragraph

sys.path.insert(0, os.path.dirname(__file__))
import gen_review as R
import gen_proposal as P

TITLE = R.TITLE
CITE = re.compile(r"(\[\d+(?:[,，\-–]\d+)*\])")
W = qn


def is_red(r):
    c = r.find(W("w:rPr") + "/" + W("w:color"))
    return c is not None and c.get(W("w:val"), "").upper() == "FF0000"


def runs(p):
    return p.findall(W("w:r"))


def rtext(r):
    return "".join(t.text or "" for t in r.iter(W("w:t")))


def set_rtext(r, s):
    ts = list(r.iter(W("w:t")))
    if not ts:
        t = OxmlElement("w:t")
        r.append(t)
        ts = [t]
    ts[0].text = s
    ts[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    for t in ts[1:]:
        t.getparent().remove(t)


def ptext(p):
    return "".join(rtext(r) for r in runs(p))


def clear_text(p):
    for t in p.iter(W("w:t")):
        t.text = ""


def drop_red(p):
    for r in runs(p):
        if is_red(r):
            p.remove(r)


def replace_in(p, old, new):
    if old not in ptext(p):
        return
    for r in runs(p):
        if old in rtext(r):
            set_rtext(r, rtext(r).replace(old, new))
            return
    rs = runs(p)
    set_rtext(rs[0], ptext(p).replace(old, new))
    for r in rs[1:]:
        p.remove(r)


def width(s):
    return sum(2 if ord(c) > 127 else 1 for c in s)


def fill_blank(p, value):
    """把下划线空格段替换为居中的取值，保持下划线长度；取值过长时去掉首行缩进以免换行。"""
    cands = [r for r in runs(p) if r.find(W("w:rPr") + "/" + W("w:u")) is not None and not rtext(r).strip()]
    r = max(cands, key=lambda x: len(rtext(x)))
    n = sum(len(rtext(x)) for x in cands)
    w = width(value)
    if n - w >= 4:
        left = (n - w) // 2
        s = " " * left + value + " " * (n - w - left)
    else:
        s = value
        ppr = p.find(W("w:pPr"))
        for el in ppr.findall(W("w:ind")):
            ppr.remove(el)
        for x in runs(p):
            if not rtext(x).strip() and x not in cands:
                set_rtext(x, " ")
    set_rtext(r, s)
    for x in cands:
        if x is not r:
            p.remove(x)


def rpr_of(p):
    for r in runs(p):
        rp = r.find(W("w:rPr"))
        if rp is not None:
            return copy.deepcopy(rp)
    return OxmlElement("w:rPr")


def set_flag(rpr, tag, on):
    for el in rpr.findall(W(tag)):
        rpr.remove(el)
    if on:
        rpr.append(OxmlElement(tag))


def set_size(rpr, half_points):
    for tag in ("w:sz", "w:szCs"):
        for el in rpr.findall(W(tag)):
            rpr.remove(el)
        el = OxmlElement(tag)
        el.set(W("w:val"), str(half_points))
        rpr.append(el)


def clean_rpr(rpr):
    for tag in ("w:color", "w:u", "w:vertAlign", "w:highlight"):
        for el in rpr.findall(W(tag)):
            rpr.remove(el)
    return rpr


def add_runs(p, text, rpr, cite=True):
    parts = CITE.split(text) if cite else [text]
    for part in parts:
        if not part:
            continue
        r = OxmlElement("w:r")
        rp = copy.deepcopy(rpr)
        if cite and CITE.fullmatch(part):
            va = OxmlElement("w:vertAlign")
            va.set(W("w:val"), "superscript")
            rp.append(va)
        r.append(rp)
        t = OxmlElement("w:t")
        t.text = part
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        r.append(t)
        p.append(r)


def new_par(template, text, bold=False, size=None, indent=True, hanging=None, cite=True):
    p = copy.deepcopy(template)
    rpr = clean_rpr(rpr_of(p))
    for r in runs(p):
        p.remove(r)
    for tag in ("w:hyperlink", "w:bookmarkStart", "w:bookmarkEnd", "w:proofErr"):
        for el in p.findall(W(tag)):
            p.remove(el)
    set_flag(rpr, "w:b", bold)
    set_flag(rpr, "w:bCs", bold)
    if size:
        set_size(rpr, size)
    ppr = p.find(W("w:pPr"))
    if ppr is None:
        ppr = OxmlElement("w:pPr")
        p.insert(0, ppr)
    for el in ppr.findall(W("w:pageBreakBefore")):
        ppr.remove(el)
    for el in ppr.findall(W("w:ind")):
        ppr.remove(el)
    ind = OxmlElement("w:ind")
    if hanging:
        ind.set(W("w:left"), str(hanging))
        ind.set(W("w:hanging"), str(hanging))
    elif indent:
        ind.set(W("w:firstLineChars"), "200")
        ind.set(W("w:firstLine"), "480")
    else:
        ind.set(W("w:firstLine"), "0")
    rpr_p = ppr.find(W("w:rPr"))
    if rpr_p is not None:
        ppr.insert(list(ppr).index(rpr_p), ind)
    else:
        ppr.append(ind)
    add_runs(p, text, rpr, cite)
    return p


def page_break_before(p):
    ppr = p.find(W("w:pPr"))
    if ppr is None:
        ppr = OxmlElement("w:pPr")
        p.insert(0, ppr)
    if ppr.find(W("w:pageBreakBefore")) is None:
        ppr.insert(0, OxmlElement("w:pageBreakBefore"))


def has_break(el):
    return any(b.get(W("w:type")) == "page" for b in el.iter(W("w:br"))) or el.find(".//" + W("w:sectPr")) is not None


def set_line_spacing(p, line=360):
    ppr = p.find(W("w:pPr"))
    for el in ppr.findall(W("w:spacing")):
        ppr.remove(el)
    sp = OxmlElement("w:spacing")
    sp.set(W("w:line"), str(line))
    sp.set(W("w:lineRule"), "auto")
    sp.set(W("w:before"), "0")
    sp.set(W("w:after"), "0")
    ppr.insert(0, sp)


def find(body, start, pred):
    for i in range(start, len(body)):
        if body[i].tag == W("w:p") and pred(ptext(body[i])):
            return i
    raise ValueError("not found")


def unique_cells(row):
    out, seen = [], set()
    for c in row.cells:
        if id(c._tc) in seen:
            continue
        seen.add(id(c._tc))
        out.append(c)
    return out


def set_cell(cell, text, rpr):
    p = cell.paragraphs[0]._p
    for r in runs(p):
        p.remove(r)
    add_runs(p, text, clean_rpr(copy.deepcopy(rpr)), cite=False)


TASK = [
    ("1.题目", [TITLE]),
    ("2.主要内容和基本要求", [
        "主要内容：",
        "（1）查阅法律人工智能、大语言模型智能体、检索增强生成及Web系统开发方面的文献，完成文献综述和开题报告，明确系统的总体方案和技术路线。",
        "（2）在扣子（Coze）平台上设计并搭建法律咨询智能体：编写角色与回复规则，要求答复包含问题分析、法律依据、处理建议和风险提示，对非法律问题礼貌拒答，对复杂问题建议咨询律师；从国家法律法规数据库获取劳动、合同、婚姻家庭、消费维权、道路交通等领域的现行法律文本，按条整理为知识库并挂载到智能体；调试后发布为API服务。",
        "（3）采用Spring Boot、MyBatis-Plus、Spring Security与JWT、Vue3、Element Plus和MySQL开发前后端分离的Web系统，面向咨询用户、律师和管理员三类角色，实现注册登录与权限控制、智能咨询（流式输出、多轮会话、咨询记录）、法条查询、律师认证与预约、后台用户管理、律师审核、数据维护和统计等功能。",
        "（4）由后端统一调用Coze开放接口，访问令牌只保存在后端，以SSE方式将智能体答复实时推送给前端，并处理超时和异常情况。",
        "（5）对系统进行功能测试和性能测试；自建法律问题测试集，对智能体法律依据引用的正确性、非法律问题拒答和答复格式进行测试，并与不挂载知识库的智能体进行对照，分析结果与不足。",
        "（6）按学校撰写规范完成毕业论文，准备答辩材料。",
        "基本要求：",
        "（1）系统能够稳定运行，各功能模块完整可用，智能体答复须给出法律依据和风险提示，并注明内容仅供参考。",
        "（2）测试数据须来自实际测试，法律条文以官方发布的文本为准，如实记录和分析测试结果。",
        "（3）论文正文不少于1万字，结构完整、条理清楚、图表规范；参考文献不少于10篇，其中外文文献不少于2篇，按GB/T 7714著录；中文摘要300～500字。",
        "（4）论文文字复制比不超过20%，按要求完成查重和AIGC检测。",
        "（5）按学校时间节点完成开题、中期检查、论文定稿和答辩，定期向指导教师汇报进展。",
    ]),
    ("3.计划进度", [
        "2026年10月下旬—2026年11月下旬：查阅文献，完成文献综述、开题报告和开题答辩；",
        "2026年11月下旬—2026年12月中旬：完成需求分析和系统设计，整理法律知识库，在Coze平台上搭建并调试智能体；",
        "2026年12月中旬—2027年1月上旬：完成系统前后端开发和智能体接入，参加中期检查；",
        "2027年1月上旬—2027年2月中旬：完成功能测试、性能测试和智能体效果测试，完成论文初稿；",
        "2027年2月中旬—2027年3月中旬：修改论文，完成查重与检测；",
        "2027年3月下旬—2027年5月上旬：论文定稿，准备答辩材料，参加答辩（5月9日前）。",
    ]),
    ("4.推荐参考文献", [
        "王禄生. ChatGPT类技术：法律人工智能的改进者还是颠覆者？[J]. 政法论坛, 2023, 41(4): 49-62.",
        "龚善要. 生成式人工智能赋能公共法律服务的范式转型[J]. 东方法学, 2024(5): 88-100.",
        "Dahl M, Magesh V, Suzgun M, et al. Large legal fictions: profiling legal hallucinations in large language models[J]. Journal of Legal Analysis, 2024, 16(1): 64-93.",
        "Wang L, Ma C, Feng X, et al. A survey on large language model based autonomous agents[J]. Frontiers of Computer Science, 2024, 18(6): 186345.",
        "Lewis P, Perez E, Piktus A, et al. Retrieval-augmented generation for knowledge-intensive NLP tasks[C]//Advances in Neural Information Processing Systems 33. 2020.",
        "任海玉, 刘建平, 王健, 等. 基于大语言模型的智能问答系统研究综述[J]. 计算机工程与应用, 2025, 61(7): 1-24.",
        "郭全中, 曾婉琪. 从辅助到自主：垂直AI智能体的现状、影响与发展趋势[J]. 新闻爱好者, 2025(10): 18-23.",
        "马雪山, 张辉军, 陈辉, 等. 前后端分离的Web平台技术研究与实现[J]. 电子技术与软件工程, 2022(8): 70-73.",
    ]),
]


def fill_task(table):
    for row, (head, items) in zip(table.rows, TASK):
        cell = unique_cells(row)[0]
        paras = [x._p for x in cell.paragraphs]
        h = paras[0]
        tmpl = copy.deepcopy(h)
        for x in paras[1:]:
            x.getparent().remove(x)
        drop_red(h)
        rs = runs(h)
        set_rtext(rs[0], head)
        for r in rs[1:]:
            h.remove(r)
        last = h
        is_ref = head.startswith("4.")
        for n, t in enumerate(items, 1):
            if is_ref:
                np_ = new_par(tmpl, f"[{n}] {t}", size=21, hanging=525, cite=False)
            elif t.endswith("：") and len(t) < 8:
                np_ = new_par(tmpl, t, bold=True, size=24, indent=False, cite=False)
            else:
                np_ = new_par(tmpl, t, size=24, indent=not head.startswith("1."), cite=False)
            set_line_spacing(np_)
            last.addnext(np_)
            last = np_


def build(src, out):
    d = docx.Document(src)
    body = list(d.element.body.iterchildren())
    a3 = find(body, 0, lambda t: t.startswith("附件材料（填写"))
    a3 = find(body, a3 + 1, lambda t: t.strip() == "附件3：")

    # 附件3：附件材料封面
    clear_text(body[a3])
    i = find(body, a3, lambda t: t.strip() == "本科毕业设计")
    replace_in(body[i], "本科毕业设计", "本科毕业论文")
    i = find(body, i, lambda t: t.startswith("毕业设计题目"))
    p = body[i]
    drop_red(p)
    rs = runs(p)
    set_rtext(rs[0], "毕业论文题目")
    set_rtext(rs[1], TITLE)
    rs[1].insert(1, OxmlElement("w:br"))
    for r in rs[2:]:
        p.remove(r)
    ppr = p.find(W("w:pPr"))
    for el in ppr.findall(W("w:ind")) + ppr.findall(W("w:jc")):
        ppr.remove(el)
    jc = OxmlElement("w:jc")
    jc.set(W("w:val"), "center")
    ppr.append(jc)
    for r in runs(body[i + 1]):
        body[i + 1].remove(r)
    i = find(body, i, lambda t: t.startswith("学       院"))
    drop_red(body[i])
    i = find(body, i, lambda t: t.startswith("专       业"))
    fill_blank(body[i], "智能科学与技术")
    j = find(body, i, lambda t: t.strip().startswith("年"))
    if not ptext(body[j - 1]).strip() and not has_break(body[j - 1]):
        body[j - 1].getparent().remove(body[j - 1])

    # 附件4：任务书封面与正文
    a4 = find(body, i, lambda t: t.strip() == "附件4：")
    clear_text(body[a4])
    i = find(body, a4, lambda t: t.strip() == "本科毕业设计任务书")
    replace_in(body[i], "本科毕业设计任务书", "本科毕业论文任务书")
    i = find(body, i, lambda t: t.strip().startswith("论文题目"))
    fill_blank(body[i], TITLE)
    i = find(body, i, lambda t: t.replace(" ", "") == "说明")
    page_break_before(body[i])
    k = find(body, i, lambda t: t.replace(" ", "") == "任务书")
    tbl4 = next(el for el in body[k:] if el.tag == W("w:tbl"))
    fill_task(Table(tbl4, d))

    # 附件5：文献综述
    a5 = find(body, i, lambda t: t.strip() == "附件5：")
    clear_text(body[a5])
    i = find(body, a5, lambda t: t.strip() == "本科毕业设计文献综述")
    replace_in(body[i], "本科毕业设计文献综述", "本科毕业论文文献综述")
    i = find(body, i, lambda t: t.strip().startswith("论文题目"))
    fill_blank(body[i], TITLE)
    h0 = find(body, i, lambda t: t.startswith("一、引言"))
    h1 = find(body, h0, lambda t: t.startswith("二、研究意义"))
    a6 = find(body, h1, lambda t: t.strip() == "附件6：")
    head_t, body_t = copy.deepcopy(body[h1]), copy.deepcopy(body[h1 + 1])
    kept_break = False
    for el in body[h0:a6]:
        if has_break(el):
            kept_break = True
            continue
        el.getparent().remove(el)
    anchor = body[a6]
    new = []
    for h, ps in R.SECTIONS:
        new.append(new_par(head_t, h, bold=True, indent=False, cite=False))
        for t in ps:
            if t.startswith("（") and len(t) < 30:
                new.append(new_par(body_t, t, bold=True))
            else:
                new.append(new_par(body_t, t))
    new.append(new_par(head_t, "七、参考文献", bold=True, indent=False, cite=False))
    for k, ref in enumerate(R.REFS, 1):
        new.append(new_par(body_t, f"[{k}] {ref}", size=21, hanging=525, cite=False))
    page_break_before(new[0])
    for el in new:
        anchor.addprevious(el)
    if not kept_break:
        page_break_before(anchor)
    clear_text(anchor)

    # 附件6：开题报告
    body = list(d.element.body.iterchildren())
    a6 = body.index(anchor)
    i = find(body, a6, lambda t: t.strip() == "本科毕业设计开题报告")
    replace_in(body[i], "本科毕业设计开题报告", "本科毕业论文开题报告")
    i = find(body, i, lambda t: t.strip().startswith("论文题目"))
    fill_blank(body[i], TITLE)
    page_break_before(body[find(body, i, lambda t: t.replace(" ", "") == "说明")])
    k = find(body, i, lambda t: t.replace(" ", "") == "开题报告")
    tbl = next(el for el in body[k:] if el.tag == W("w:tbl"))
    table = Table(tbl, d)
    contents = [ps for _, ps in P.SECTIONS] + [[f"[{n}] {ref}" for n, ref in enumerate(P.REFS, 1)]]
    for row, ps in zip(table.rows, contents):
        cell = unique_cells(row)[0]
        paras = [x._p for x in cell.paragraphs]
        head = paras[0]
        for x in paras[1:]:
            x.getparent().remove(x)
        tmpl = copy.deepcopy(head)
        last = head
        for t in ps:
            if t.startswith("[") and re.match(r"^\[\d+\] ", t):
                np_ = new_par(tmpl, t, size=21, hanging=525, cite=False)
            elif re.match(r"^（\d）", t):
                np_ = new_par(tmpl, t, bold=True, size=24, indent=False)
            else:
                np_ = new_par(tmpl, t, size=24)
            set_line_spacing(np_)
            last.addnext(np_)
            last = np_

    # 附件8：中期检查表（学生部分）
    body = list(d.element.body.iterchildren())
    a8 = find(body, body.index(tbl), lambda t: t.strip() == "附件8：")
    clear_text(body[a8])
    i = find(body, a8, lambda t: "中期检查表" in t)
    replace_in(body[i], "本科毕业设计中期检查表", "本科毕业论文中期检查表")
    tbl8 = next(el for el in body[i:] if el.tag == W("w:tbl"))
    t8 = Table(tbl8, d)
    lab = rpr_of(unique_cells(t8.rows[0])[0].paragraphs[0]._p)
    c = unique_cells(t8.rows[3])
    set_cell(c[1], TITLE, lab)
    c = unique_cells(t8.rows[4])
    set_cell(c[1], "否", lab)
    set_cell(c[3], "无", lab)
    c = unique_cells(t8.rows[5])
    for j in (1, 3, 5):
        set_cell(c[j], "是", lab)
    c = unique_cells(t8.rows[6])
    set_cell(c[1], "以现行法律条文为知识库约束智能体的答复依据，减少法律幻觉；后端以流式方式接入扣子智能体并管理多轮会话；通过对照实验检验知识库的作用。", lab)
    set_cell(c[3], "2027年4月", lab)
    cell = unique_cells(t8.rows[7])[0]
    paras = [x._p for x in cell.paragraphs]
    replace_in(paras[0], "毕业设计进度情况", "毕业论文进度情况")
    progress = ("已完成文献综述和开题报告。在扣子平台搭建并发布了法律咨询智能体，从国家法律法规数据库整理6部现行法律共1706条条文作为知识库；"
                "完成Spring Boot后端和Vue3前端开发并接入智能体，实现了智能咨询、咨询记录、法条查询、律师预约和后台管理等功能；"
                "完成功能测试（28项全部通过）、性能测试和智能体问答效果测试（挂载知识库的智能体法律依据正确43/50，对照组39/50）；"
                "论文初稿已完成，正在根据指导教师意见修改。")
    tgt = paras[1] if len(paras) > 1 else paras[0]
    for r in runs(tgt):
        tgt.remove(r)
    add_runs(tgt, progress, clean_rpr(copy.deepcopy(lab)), cite=False)
    d.save(out)


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.environ["TEMP"], "handbook.docx")
    out = os.path.join(os.path.dirname(__file__), "..", "交付", "指导手册_学生填写部分.docx")
    build(src, out)
    print("saved", os.path.abspath(out))
