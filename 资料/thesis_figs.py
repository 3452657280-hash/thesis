"""用 Pillow 绘制论文中的结构图、时序图与统计图，输出到 交付/论文图片/。数据图的数值取自测试结果文件。"""
import csv
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "交付", "论文图片")
os.makedirs(OUT, exist_ok=True)
FONT = r"C:\Windows\Fonts\simhei.ttf"
S = 2


def f(size):
    return ImageFont.truetype(FONT, size * S)


def canvas(w, h):
    im = Image.new("RGB", (w * S, h * S), "white")
    return im, ImageDraw.Draw(im)


def box(d, x, y, w, h, text, size=16, fill="#FFFFFF", bold=False, radius=6):
    d.rounded_rectangle([x * S, y * S, (x + w) * S, (y + h) * S], radius=radius * S, outline="black",
                        width=(3 if bold else 2), fill=fill)
    lines = text.split("\n")
    ft = f(size)
    lh = size * 1.35
    top = y + (h - lh * len(lines)) / 2
    for i, ln in enumerate(lines):
        tw = d.textlength(ln, font=ft) / S
        d.text(((x + (w - tw) / 2) * S, (top + i * lh) * S), ln, fill="black", font=ft)


def text(d, x, y, s, size=14, anchor="la"):
    d.text((x * S, y * S), s, fill="black", font=f(size), anchor=anchor)


def arrow(d, x1, y1, x2, y2, label=None, size=13, dash=False, both=False):
    import math
    if dash:
        n = int(math.hypot(x2 - x1, y2 - y1) / 8)
        for i in range(0, n, 2):
            a, b = i / n, min(1, (i + 1) / n)
            d.line([((x1 + (x2 - x1) * a) * S, (y1 + (y2 - y1) * a) * S),
                    ((x1 + (x2 - x1) * b) * S, (y1 + (y2 - y1) * b) * S)], fill="black", width=2)
    else:
        d.line([(x1 * S, y1 * S), (x2 * S, y2 * S)], fill="black", width=2)

    def head(xa, ya, xb, yb):
        ang = math.atan2(yb - ya, xb - xa)
        p = [(xb, yb), (xb - 10 * math.cos(ang - 0.4), yb - 10 * math.sin(ang - 0.4)),
             (xb - 10 * math.cos(ang + 0.4), yb - 10 * math.sin(ang + 0.4))]
        d.polygon([(a * S, b * S) for a, b in p], fill="black")
    head(x1, y1, x2, y2)
    if both:
        head(x2, y2, x1, y1)
    if label:
        text(d, (x1 + x2) / 2, (y1 + y2) / 2 - 4, label, size, anchor="md")


def save(im, name):
    im.save(os.path.join(OUT, name), dpi=(300, 300))


def fig_arch():
    im, d = canvas(900, 560)
    layers = [
        ("表现层", "Vue 3 + Element Plus + Vue Router + Pinia + ECharts\n咨询用户端 / 律师端 / 管理员端页面"),
        ("接口层", "Spring MVC 控制器（RESTful 接口、SSE 流式接口）\nSpring Security + JWT 认证与角色鉴权"),
        ("业务层", "用户、智能咨询、法条、文书模板、律师预约、后台管理等服务\nCozeClient：调用智能体、解析流式事件"),
        ("数据层", "MyBatis-Plus 数据访问\nMySQL 8.0（开发测试使用 H2 MySQL 兼容模式）"),
    ]
    y = 30
    for name, desc in layers:
        box(d, 30, y, 110, 90, name, 18, "#EAF1FB", True)
        box(d, 150, y, 470, 90, desc, 15)
        y += 120
    for i in range(3):
        arrow(d, 385, 120 + i * 120, 385, 150 + i * 120, both=True)
    box(d, 680, 150, 190, 330, "Coze 平台\n\n法律咨询助手\n（单 Agent）\n\n人设与回复逻辑\n大模型：豆包·2.0·pro\n知识库：中国法律条文库\n6 部法律 1706 条", 15, "#FFF4E0", True)
    arrow(d, 620, 315, 680, 315, both=True)
    text(d, 650, 290, "HTTPS", 13, "md")
    text(d, 650, 345, "Chat v3 / SSE", 13, "md")
    save(im, "图3-1_系统总体架构图.png")


def fig_modules():
    im, d = canvas(1000, 470)
    box(d, 380, 20, 240, 50, "基于Coze智能体的法律咨询系统", 16, "#EAF1FB", True)
    groups = [
        ("咨询用户端", ["注册登录", "智能咨询", "会话管理", "法条查询", "文书模板", "律师预约", "收藏与评价", "个人中心"]),
        ("律师端", ["资质认证", "预约处理", "咨询回复", "个人中心"]),
        ("管理员端", ["数据统计", "用户管理", "律师审核", "法条管理", "模板管理", "公告管理", "问答记录"]),
    ]
    xs = [40, 400, 640]
    widths = [8, 4, 7]
    d.line([(500 * S, 70 * S), (500 * S, 100 * S)], fill="black", width=2)
    centers = []
    for (g, items), x0, n in zip(groups, xs, widths):
        cx = x0 + n * 42 / 2
        centers.append(cx)
        box(d, cx - 60, 130, 120, 40, g, 15, "#F2F2F2", True)
        d.line([(cx * S, 170 * S), (cx * S, 195 * S)], fill="black", width=2)
        d.line([((x0 + 16) * S, 195 * S), ((x0 + (n - 1) * 42 + 16) * S, 195 * S)], fill="black", width=2)
        for i, it in enumerate(items):
            x = x0 + i * 42
            d.line([((x + 16) * S, 195 * S), ((x + 16) * S, 215 * S)], fill="black", width=2)
            d.rectangle([(x + 2) * S, 215 * S, (x + 30) * S, 420 * S], outline="black", width=2)
            ft = f(14)
            for j, ch in enumerate(it):
                tw = d.textlength(ch, font=ft) / S
                d.text(((x + 16 - tw / 2) * S, (228 + j * 22) * S), ch, fill="black", font=ft)
    d.line([(centers[0] * S, 100 * S), (centers[-1] * S, 100 * S)], fill="black", width=2)
    for cx in centers:
        d.line([(cx * S, 100 * S), (cx * S, 130 * S)], fill="black", width=2)
    save(im, "图3-2_系统功能模块图.png")


def fig_agent():
    im, d = canvas(900, 430)
    box(d, 20, 170, 120, 70, "用户问题\n（经后端转发）", 15)
    box(d, 190, 40, 520, 340, "", 15, "#FFFBF2", True)
    text(d, 450, 52, "Coze 智能体：法律咨询助手", 16, "ma")
    box(d, 215, 90, 210, 120, "人设与回复逻辑\n角色定位与回答范围\n四段式答复结构\n拒答、转律师与免责规则", 14, "#EAF1FB")
    box(d, 475, 90, 210, 120, "大语言模型\n豆包·2.0·pro\n精确模式，关闭深度思考\n上下文 3 轮", 14, "#EAF1FB")
    box(d, 475, 250, 210, 105, "知识库（自动调用）\n中国法律条文库\n6 部法律，1706 个片段\n一条法条为一个分段", 14, "#EAF1FB")
    box(d, 215, 250, 210, 105, "领域识别\n劳动用工 / 婚姻家庭\n合同纠纷 / 消费维权\n交通事故 / 非法律问题", 14, "#EAF1FB")
    arrow(d, 425, 150, 475, 150)
    arrow(d, 580, 210, 580, 250, both=True)
    text(d, 590, 233, "检索与召回", 13)
    arrow(d, 425, 300, 475, 300)
    arrow(d, 320, 210, 320, 250)
    arrow(d, 140, 205, 215, 205)
    box(d, 750, 150, 130, 110, "结构化回答\n问题分析\n法律依据\n处理建议\n风险提示", 14)
    arrow(d, 710, 205, 750, 205)
    save(im, "图3-3_法律咨询智能体结构图.png")


def fig_seq():
    im, d = canvas(980, 640)
    names = ["用户", "前端页面", "后端服务", "Coze 智能体", "数据库"]
    xs = [70, 260, 470, 690, 890]
    for n, x in zip(names, xs):
        box(d, x - 60, 20, 120, 40, n, 15, "#EAF1FB", True)
        y = 60
        while y < 620:
            d.line([(x * S, y * S), (x * S, (y + 6) * S)], fill="black", width=2)
            y += 12
    msgs = [
        (0, 1, "输入问题并发送", False),
        (1, 2, "POST /sessions/{id}/chat（携带JWT）", False),
        (2, 4, "校验会话归属，保存用户消息", False),
        (2, 3, "POST /v3/chat（Bearer 令牌，stream=true）", False),
        (3, 3, "检索知识库，生成回答", False),
        (3, 2, "SSE：conversation.message.delta …", True),
        (2, 1, "SSE：delta 增量文本", True),
        (1, 0, "逐字渲染 Markdown", True),
        (3, 2, "conversation.message.completed / chat.completed", True),
        (2, 4, "保存回答、耗时与 conversation_id", False),
        (2, 1, "SSE：done（消息ID、首字与总耗时）", True),
        (1, 0, "显示收藏、评价按钮", True),
    ]
    y = 95
    for a, b, label, back in msgs:
        if a == b:
            x = xs[a]
            d.line([(x * S, y * S), ((x + 50) * S, y * S), ((x + 50) * S, (y + 22) * S)], fill="black", width=2)
            arrow(d, x + 50, y + 22, x + 2, y + 22)
            text(d, x + 56, y + 4, label, 13)
            y += 48
            continue
        arrow(d, xs[a], y, xs[b], y, dash=back)
        text(d, (xs[a] + xs[b]) / 2, y - 5, label, 13, "md")
        y += 42
    save(im, "图3-4_智能咨询时序图.png")


def fig_er():
    im, d = canvas(960, 520)
    E = {
        "sys_user": (380, 30, "用户\nsys_user"),
        "lawyer_profile": (720, 30, "律师资质\nlawyer_profile"),
        "consult_session": (60, 200, "咨询会话\nconsult_session"),
        "consult_message": (60, 400, "咨询消息\nconsult_message"),
        "appointment": (720, 220, "律师预约\nappointment"),
        "feedback": (380, 400, "回答评价\nfeedback"),
        "favorite": (380, 230, "收藏\nfavorite"),
    }
    W, H = 170, 60

    def edge(cx, cy, tx, ty):
        dx, dy = tx - cx, ty - cy
        t = min((W / 2) / abs(dx) if dx else 1e9, (H / 2) / abs(dy) if dy else 1e9)
        return cx + dx * t, cy + dy * t

    links = [("sys_user", "lawyer_profile", "1", "1", "认证"), ("sys_user", "consult_session", "1", "N", "拥有"),
             ("consult_session", "consult_message", "1", "N", "包含"), ("lawyer_profile", "appointment", "1", "N", "受理"),
             ("sys_user", "appointment", "1", "N", "发起"), ("consult_message", "feedback", "1", "N", "评价"),
             ("sys_user", "favorite", "1", "N", "收藏")]
    geo = []
    for a, b, la, lb, mid in links:
        c1 = (E[a][0] + W / 2, E[a][1] + H / 2)
        c2 = (E[b][0] + W / 2, E[b][1] + H / 2)
        p1, p2 = edge(*c1, *c2), edge(*c2, *c1)
        d.line([(p1[0] * S, p1[1] * S), (p2[0] * S, p2[1] * S)], fill="black", width=2)
        geo.append((p1, p2, la, lb, mid))
    for k, (x, y, t) in E.items():
        box(d, x, y, W, H, t, 15, "#EAF1FB", True, 2)
    for p1, p2, la, lb, mid in geo:
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        d.polygon([((mx - 34) * S, my * S), (mx * S, (my - 18) * S), ((mx + 34) * S, my * S), (mx * S, (my + 18) * S)],
                  fill="white", outline="black")
        text(d, mx, my, mid, 13, "mm")
        for p, q, lab in ((p1, p2, la), (p2, p1, lb)):
            lx, ly = p[0] + (q[0] - p[0]) * 0.12, p[1] + (q[1] - p[1]) * 0.12
            text(d, lx + 10, ly - 8, lab, 14, "mm")
    text(d, 480, 495, "注：法条表 law_article、文书模板表 doc_template、公告表 notice 为独立实体，图中从略", 13, "mm")
    save(im, "图3-5_系统总体E-R图.png")


def fig_bar():
    path = os.path.join(ROOT, "测试", "results_kb_20261103_153932_judged.csv")
    with open(path, encoding="utf-8-sig") as fh:
        rows = [r for r in csv.DictReader(fh) if r["category"] != "非法律问题"]
    cats = ["劳动用工", "婚姻家庭", "合同纠纷", "消费维权", "交通事故"]
    vals = [sum(r["judge_law_correct"] == "1" for r in rows if r["category"] == c) for c in cats]
    im, d = canvas(720, 420)
    x0, y0, h = 80, 360, 280
    d.line([(x0 * S, y0 * S), (680 * S, y0 * S)], fill="black", width=2)
    d.line([(x0 * S, y0 * S), (x0 * S, (y0 - h - 20) * S)], fill="black", width=2)
    for k in range(0, 11, 2):
        y = y0 - h * k / 10
        d.line([((x0 - 5) * S, y * S), (x0 * S, y * S)], fill="black", width=2)
        text(d, x0 - 10, y, str(k), 13, "rm")
    text(d, 30, 60, "正确题数", 13, "la")
    for i, (c, v) in enumerate(zip(cats, vals)):
        x = x0 + 30 + i * 118
        d.rectangle([x * S, (y0 - h * v / 10) * S, (x + 60) * S, y0 * S], fill="#7F9FCB", outline="black", width=2)
        text(d, x + 30, y0 - h * v / 10 - 6, f"{v}/10", 14, "md")
        text(d, x + 30, y0 + 22, c, 14, "mm")
    save(im, "图5-1_各类别法律依据正确题数.png")
    return dict(zip(cats, vals))


def actor(d, cx, top, name):
    d.ellipse([(cx - 12) * S, top * S, (cx + 12) * S, (top + 24) * S], outline="black", width=2)
    d.line([(cx * S, (top + 24) * S), (cx * S, (top + 62) * S)], fill="black", width=2)
    d.line([((cx - 22) * S, (top + 36) * S), ((cx + 22) * S, (top + 36) * S)], fill="black", width=2)
    d.line([(cx * S, (top + 62) * S), ((cx - 18) * S, (top + 90) * S)], fill="black", width=2)
    d.line([(cx * S, (top + 62) * S), ((cx + 18) * S, (top + 90) * S)], fill="black", width=2)
    text(d, cx, top + 106, name, 15, "mm")


def ellipse(d, cx, cy, w, h, s, size=14):
    d.ellipse([(cx - w / 2) * S, (cy - h / 2) * S, (cx + w / 2) * S, (cy + h / 2) * S], outline="black", width=2, fill="white")
    text(d, cx, cy, s, size, "mm")


def fig_usecase():
    im, d = canvas(1000, 640)
    d.rectangle([180 * S, 20 * S, 820 * S, 620 * S], outline="black", width=2)
    text(d, 500, 38, "基于Coze智能体的法律咨询系统", 15, "mm")
    groups = [
        ("咨询用户", 110, ["注册登录", "智能咨询（多轮）", "会话管理", "收藏与评价回答", "法条查询", "下载文书模板", "预约律师", "查看预约结果"]),
        ("律师", 890, ["提交资质认证", "处理预约", "填写咨询回复"]),
        ("管理员", 890, ["查看统计看板", "用户管理", "律师资质审核", "法条与模板维护", "查看问答记录"]),
    ]
    left = groups[0]
    actor(d, left[1], 230, left[0])
    for i, uc in enumerate(left[2]):
        cy = 75 + i * 68
        ellipse(d, 340, cy, 210, 46, uc)
        d.line([((left[1] + 24) * S, 280 * S), ((340 - 105) * S, cy * S)], fill="black", width=2)
    ellipse(d, 540, 245, 170, 46, "Coze智能体问答", 13)
    arrow(d, 400, 165, 500, 223, dash=True)
    text(d, 470, 180, "<<include>>", 11, "mm")
    actor(d, 890, 70, "律师")
    for i, uc in enumerate(groups[1][2]):
        cy = 70 + i * 62
        ellipse(d, 680, cy, 200, 46, uc)
        d.line([((890 - 24) * S, 120 * S), ((680 + 100) * S, cy * S)], fill="black", width=2)
    actor(d, 890, 380, "管理员")
    for i, uc in enumerate(groups[2][2]):
        cy = 330 + i * 62
        ellipse(d, 680, cy, 200, 46, uc)
        d.line([((890 - 24) * S, 430 * S), ((680 + 100) * S, cy * S)], fill="black", width=2)
    save(im, "用例图.png")


def fig_state():
    im, d = canvas(900, 380)
    d.ellipse([30 * S, 175 * S, 54 * S, 199 * S], fill="black")
    box(d, 130, 160, 130, 54, "待处理\n(status=0)", 15, "#EAF1FB", True, 20)
    box(d, 420, 60, 130, 54, "已接受\n(status=1)", 15, "#EAF1FB", True, 20)
    box(d, 420, 260, 130, 54, "已拒绝\n(status=2)", 15, "#EAF1FB", True, 20)
    box(d, 680, 160, 130, 54, "已完成\n(status=3)", 15, "#EAF1FB", True, 20)
    for cx, cy in ((485, 350), (840, 187)):
        d.ellipse([(cx - 13) * S, (cy - 13) * S, (cx + 13) * S, (cy + 13) * S], outline="black", width=2)
        d.ellipse([(cx - 8) * S, (cy - 8) * S, (cx + 8) * S, (cy + 8) * S], fill="black")
    arrow(d, 54, 187, 130, 187, "用户提交预约", 12)
    arrow(d, 260, 175, 420, 95, "律师接受", 13)
    arrow(d, 260, 200, 420, 280, "律师拒绝", 13)
    arrow(d, 260, 187, 680, 187, "律师直接完成", 13)
    arrow(d, 550, 95, 680, 172, "咨询完成并回复", 13)
    arrow(d, 485, 314, 485, 337)
    arrow(d, 810, 187, 827, 187)
    text(d, 450, 30, "已拒绝、已完成为终态，后端拒绝其他任何状态变更", 13, "mm")
    save(im, "预约状态图.png")


def fig_flow():
    im, d = canvas(760, 900)
    cx = 380

    def diamond(cy, s, w=230, h=64):
        d.polygon([((cx - w / 2) * S, cy * S), (cx * S, (cy - h / 2) * S), ((cx + w / 2) * S, cy * S), (cx * S, (cy + h / 2) * S)],
                  outline="black", fill="#FFF4E0", width=2)
        text(d, cx, cy, s, 14, "mm")

    box(d, cx - 70, 15, 140, 40, "开始", 15, "#F2F2F2", True, 20)
    arrow(d, cx, 55, cx, 80)
    box(d, cx - 130, 80, 260, 44, "用户在会话中输入问题并发送", 14)
    arrow(d, cx, 124, cx, 150)
    diamond(182, "会话属于当前用户？")
    arrow(d, cx, 214, cx, 240)
    text(d, cx + 14, 228, "是", 13, "lm")
    diamond(272, "该会话正在生成回答？")
    arrow(d, cx, 304, cx, 330)
    text(d, cx + 14, 318, "否", 13, "lm")
    box(d, cx - 130, 330, 260, 44, "保存用户消息，返回SSE连接", 14)
    arrow(d, cx, 374, cx, 400)
    box(d, cx - 160, 400, 320, 44, "携带conversation_id调用Coze /v3/chat", 14)
    arrow(d, cx, 444, cx, 470)
    diamond(502, "返回事件流？")
    arrow(d, cx, 534, cx, 560)
    text(d, cx + 14, 548, "是", 13, "lm")
    box(d, cx - 160, 560, 320, 44, "逐条转发delta增量，记录首字耗时", 14)
    arrow(d, cx, 604, cx, 630)
    diamond(662, "对话结束或超时？")
    arrow(d, cx, 694, cx, 720)
    text(d, cx + 14, 708, "正常结束", 13, "lm")
    box(d, cx - 160, 720, 320, 44, "保存回答、耗时与conversation_id", 14)
    arrow(d, cx, 764, cx, 790)
    box(d, cx - 130, 790, 260, 40, "推送done事件", 14)
    arrow(d, cx, 830, cx, 850)
    box(d, cx - 70, 850, 140, 38, "结束", 15, "#F2F2F2", True, 20)
    box(d, 600, 160, 140, 44, "提示会话不存在", 13)
    arrow(d, cx + 115, 182, 600, 182, "否", 13)
    box(d, 600, 250, 140, 44, "提示请等待", 13)
    arrow(d, cx + 115, 272, 600, 272, "是", 13)
    box(d, 600, 480, 140, 44, "解析错误JSON\n推送error事件", 13)
    arrow(d, cx + 115, 502, 600, 502, "否", 13)
    d.line([((cx - 115) * S, 662 * S), (60 * S, 662 * S), (60 * S, 582 * S)], fill="black", width=2)
    arrow(d, 60, 582, cx - 160, 582)
    text(d, 90, 650, "未结束", 13, "mm")
    box(d, 600, 640, 140, 44, "关闭连接\n推送error事件", 13)
    arrow(d, cx + 115, 662, 600, 662, "超时", 13)
    save(im, "智能咨询业务流程图.png")


def fig_bar2():
    files = {"kb": "results_kb_20261103_153932_judged.csv", "bl": "results_baseline_all_judged.csv"}
    data = {}
    for k, fn in files.items():
        p = os.path.join(ROOT, "测试", fn)
        if not os.path.exists(p):
            return None
        with open(p, encoding="utf-8-sig") as fh:
            data[k] = [r for r in csv.DictReader(fh) if r["category"] != "非法律问题"]
    cats = ["劳动用工", "婚姻家庭", "合同纠纷", "消费维权", "交通事故"]
    vals = {k: [sum(r["judge_law_correct"] == "1" for r in v if r["category"] == c) for c in cats] for k, v in data.items()}
    im, d = canvas(760, 440)
    x0, y0, h = 80, 360, 280
    d.line([(x0 * S, y0 * S), (720 * S, y0 * S)], fill="black", width=2)
    d.line([(x0 * S, y0 * S), (x0 * S, (y0 - h - 20) * S)], fill="black", width=2)
    for k in range(0, 11, 2):
        y = y0 - h * k / 10
        d.line([((x0 - 5) * S, y * S), (x0 * S, y * S)], fill="black", width=2)
        text(d, x0 - 10, y, str(k), 13, "rm")
    text(d, 30, 60, "正确题数", 13, "la")
    for i, c in enumerate(cats):
        x = x0 + 25 + i * 125
        for j, (k, fill) in enumerate((("kb", "#7F9FCB"), ("bl", "#D9D9D9"))):
            v = vals[k][i]
            xx = x + j * 44
            d.rectangle([xx * S, (y0 - h * v / 10) * S, (xx + 40) * S, y0 * S], fill=fill, outline="black", width=2)
            text(d, xx + 20, y0 - h * v / 10 - 6, str(v), 13, "md")
        text(d, x + 42, y0 + 22, c, 14, "mm")
    for j, (lab, fill) in enumerate((("知识库组", "#7F9FCB"), ("对照组（无知识库）", "#D9D9D9"))):
        xx = 470 + j * 120
        d.rectangle([xx * S, 40 * S, (xx + 18) * S, 54 * S], fill=fill, outline="black", width=2)
        text(d, xx + 24, 47, lab, 13, "lm")
    save(im, "图5-1_各类别法律依据正确题数.png")
    return vals


if __name__ == "__main__":
    fig_usecase()
    fig_state()
    fig_flow()
    print(fig_bar2())
    import sys
    if "--all" not in sys.argv:
        raise SystemExit
    fig_arch()
    fig_modules()
    fig_agent()
    fig_seq()
    fig_er()
    print(fig_bar())
    print("输出目录：", OUT)
