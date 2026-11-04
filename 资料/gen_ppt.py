"""生成答辩 PPT：交付/答辩PPT_基于Coze智能体的法律咨询系统的设计与实现.pptx
数字全部取自论文与测试结果，图片取自 交付/论文图片/。"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IMG = os.path.join(ROOT, "交付", "论文图片")
OUT = os.path.join(ROOT, "交付", "答辩PPT_基于Coze智能体的法律咨询系统的设计与实现.pptx")

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
BLUE = RGBColor(0x2E, 0x6F, 0xB7)
LIGHT = RGBColor(0xEE, 0xF3, 0xF9)
GRAY = RGBColor(0x55, 0x55, 0x55)
ORANGE = RGBColor(0xE0, 0x7B, 0x26)
GREEN = RGBColor(0x2E, 0x8B, 0x57)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "微软雅黑"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
W, H = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]
TOTAL = 16
page = [0]


def img(name):
    p = os.path.join(IMG, name)
    if not os.path.exists(p):
        raise FileNotFoundError(p)
    return p


def text(slide, x, y, w, h, s, size=18, bold=False, color=GRAY, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    lines = s if isinstance(s, list) else [s]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = line
        r.font.size, r.font.bold, r.font.name = Pt(size), bold, FONT
        r.font.color.rgb = color
        p.space_after = Pt(6)
    return tb


def bullets(slide, x, y, w, h, items, size=18):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        sub = it.startswith("  ")
        r = p.add_run()
        r.text = ("– " if sub else "● ") + it.strip()
        r.font.size, r.font.name = Pt(size - 2 if sub else size), FONT
        r.font.color.rgb = GRAY if sub else RGBColor(0x33, 0x33, 0x33)
        p.level = 1 if sub else 0
        p.space_after = Pt(8)
    return tb


def rect(slide, x, y, w, h, fill, line=None):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
    s.shadow.inherit = False
    return s


def picture(slide, path, x, y, maxw, maxh):
    iw, ih = Image.open(path).size
    scale = min(maxw / iw, maxh / ih)
    w, h = int(iw * scale), int(ih * scale)
    return slide.shapes.add_picture(path, x + (maxw - w) // 2, y + (maxh - h) // 2, w, h)


def new_slide(title, section=""):
    page[0] += 1
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, W, Inches(1.0), NAVY)
    text(s, Inches(0.5), Inches(0.15), Inches(10), Inches(0.75), title, 28, True, WHITE, anchor=MSO_ANCHOR.MIDDLE)
    if section:
        text(s, Inches(9.8), Inches(0.25), Inches(3.2), Inches(0.6), section, 14, False, RGBColor(0xC8, 0xD6, 0xE8), PP_ALIGN.RIGHT, MSO_ANCHOR.MIDDLE)
    rect(s, 0, H - Inches(0.35), W, Inches(0.35), LIGHT)
    text(s, Inches(0.5), H - Inches(0.36), Inches(8), Inches(0.35), "基于Coze智能体的法律咨询系统的设计与实现", 11, False, GRAY, anchor=MSO_ANCHOR.MIDDLE)
    text(s, W - Inches(1.5), H - Inches(0.36), Inches(1.0), Inches(0.35), f"{page[0]} / {TOTAL}", 11, False, GRAY, PP_ALIGN.RIGHT, MSO_ANCHOR.MIDDLE)
    return s


def card(slide, x, y, w, h, big, small, color=BLUE):
    rect(slide, x, y, w, h, LIGHT)
    rect(slide, x, y, Inches(0.08), h, color)
    text(slide, x + Inches(0.2), y + Inches(0.1), w - Inches(0.3), Inches(0.8), big, 30, True, color)
    text(slide, x + Inches(0.2), y + Inches(0.85), w - Inches(0.3), h - Inches(0.9), small, 14, False, GRAY)


def notes(slide, s):
    slide.notes_slide.notes_text_frame.text = s


# 1 封面
page[0] += 1
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, W, H, NAVY)
rect(s, 0, Inches(4.6), W, Inches(0.06), ORANGE)
text(s, Inches(0.8), Inches(1.6), Inches(11.7), Inches(1.2), "基于Coze智能体的法律咨询系统的设计与实现", 40, True, WHITE, PP_ALIGN.CENTER)
text(s, Inches(0.8), Inches(2.9), Inches(11.7), Inches(0.6), "本科毕业论文答辩", 22, False, RGBColor(0xC8, 0xD6, 0xE8), PP_ALIGN.CENTER)
text(s, Inches(0.8), Inches(4.9), Inches(11.7), Inches(1.6),
     ["学院：未来技术学院    专业：智能科学与技术", "答辩人：__________    指导教师：__________"], 20, False, WHITE, PP_ALIGN.CENTER)
notes(s, "各位老师好，我是××，我的毕业论文题目是《基于Coze智能体的法律咨询系统的设计与实现》。下面我从研究背景、系统设计、实现、测试和总结五个部分汇报。（约20秒）")

# 2 目录
s = new_slide("汇报内容")
items = ["研究背景与意义", "相关技术", "需求分析与系统设计", "智能体与系统实现", "系统测试与结果分析", "总结与不足"]
for i, it in enumerate(items):
    y = Inches(1.5) + i * Inches(0.9)
    rect(s, Inches(3.2), y, Inches(0.7), Inches(0.7), BLUE)
    text(s, Inches(3.2), y, Inches(0.7), Inches(0.7), f"{i+1:02d}", 22, True, WHITE, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    text(s, Inches(4.1), y, Inches(7), Inches(0.7), it, 24, False, RGBColor(0x33, 0x33, 0x33), anchor=MSO_ANCHOR.MIDDLE)
notes(s, "汇报分六部分。（约10秒，直接翻页）")

# 3 背景
s = new_slide("研究背景：两个现实问题", "01 研究背景")
card(s, Inches(0.6), Inches(1.4), Inches(5.9), Inches(2.4), "获取法律意见成本高",
     "欠薪、押金、网购维权等日常法律问题常见；截至2022年底全国执业律师65.16万多人，单靠人工难以回应大量基础性咨询。")
card(s, Inches(6.8), Inches(1.4), Inches(5.9), Inches(2.4), "大模型直接回答易出错",
     "Dahl等人的实证研究：大模型回答可验证的判例问题，幻觉比例至少58%。编造法条可能导致错误的维权决定。", ORANGE)
rect(s, Inches(0.6), Inches(4.2), Inches(12.1), Inches(2.4), WHITE, BLUE)
text(s, Inches(0.9), Inches(4.35), Inches(11.5), Inches(0.6), "本文思路", 22, True, NAVY)
bullets(s, Inches(0.9), Inches(4.95), Inches(11.5), Inches(1.6), [
    "用扣子（Coze）平台搭建法律咨询智能体，挂载由法条原文构成的知识库，让回答“有据可查”",
    "开发完整的Web系统（Spring Boot + Vue 3），提供咨询、法条查询、律师预约等业务功能",
    "通过对照实验，检验知识库对回答准确性和可追溯性的实际作用"], 18)
notes(s, "选题来自两个问题。一是普通人找律师成本高；二是直接用大模型回答法律问题容易编造法条，研究表明幻觉比例至少58%。所以我的思路是：用智能体加法条知识库，让回答有依据，再做成完整的系统，并用对照实验验证效果。（约1分钟）")

# 4 研究现状 & 目标
s = new_slide("研究现状与本文工作", "01 研究背景")
text(s, Inches(0.6), Inches(1.3), Inches(6), Inches(0.5), "已有研究", 22, True, NAVY)
bullets(s, Inches(0.6), Inches(1.9), Inches(6), Inches(4.5), [
    "LawBench：从记忆、理解、应用三层评测大模型法律能力",
    "DISC-LawLLM、ChatLaw：微调或多智能体增强法律问答",
    "RAG（检索增强生成）：引入外部知识减少幻觉",
    "商用法律AI工具即使用了RAG，幻觉仍在17%～33%",
    "不足：多需构造训练数据或复杂推理流程，面向公众的完整咨询系统讨论较少"], 17)
text(s, Inches(6.9), Inches(1.3), Inches(6), Inches(0.5), "本文主要工作", 22, True, NAVY)
for i, (t, d) in enumerate([("知识库", "6部现行法律按条整理为1706个片段"),
                            ("智能体", "人设约束回答结构与引用规则"),
                            ("Web系统", "前后端分离，流式代理调用，三类角色"),
                            ("测试", "功能、性能、60题效果测试与对照实验")]):
    y = Inches(1.9) + i * Inches(1.15)
    rect(s, Inches(6.9), y, Inches(1.6), Inches(0.95), BLUE)
    text(s, Inches(6.9), y, Inches(1.6), Inches(0.95), t, 18, True, WHITE, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    rect(s, Inches(8.5), y, Inches(4.2), Inches(0.95), LIGHT)
    text(s, Inches(8.65), y, Inches(4.0), Inches(0.95), d, 16, False, GRAY, anchor=MSO_ANCHOR.MIDDLE)
notes(s, "已有研究多是改进模型本身，需要构造训练数据，而面向普通人、能直接用的完整系统讨论较少。本文不训练模型，而是用平台搭智能体加知识库，重点做完整系统和效果验证。（约40秒）")

# 5 技术
s = new_slide("相关技术", "02 相关技术")
cols = [("扣子（Coze）智能体平台", ["角色设定（人设与回复逻辑）", "知识库：上传文档自动分段、检索召回", "发布为API，后端以流式方式调用"]),
        ("后端", ["Spring Boot 3 + MyBatis-Plus", "Spring Security + JWT 鉴权", "SSE 流式转发智能体回答"]),
        ("前端", ["Vue 3 + Element Plus", "Pinia 状态管理、Vue Router", "ECharts 数据看板、markdown 渲染"])]
for i, (t, its) in enumerate(cols):
    x = Inches(0.6) + i * Inches(4.15)
    rect(s, x, Inches(1.4), Inches(3.9), Inches(0.75), NAVY)
    text(s, x, Inches(1.4), Inches(3.9), Inches(0.75), t, 18, True, WHITE, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    rect(s, x, Inches(2.15), Inches(3.9), Inches(3.0), LIGHT)
    bullets(s, x + Inches(0.15), Inches(2.35), Inches(3.6), Inches(2.8), its, 16)
text(s, Inches(0.6), Inches(5.5), Inches(12.1), Inches(1.2),
     "选择扣子平台的原因：知识库、角色设定和API发布开箱即用，开发门槛低，可以把精力放在知识库质量、回答约束和系统集成上。", 17, False, NAVY)
notes(s, "技术上分三块：扣子平台负责智能体和知识库；后端Spring Boot负责业务和流式转发；前端Vue 3。选扣子是因为知识库、人设、API都现成，可以专注在知识质量和系统集成。（约40秒）")

# 6 需求
s = new_slide("需求分析：三类用户", "03 系统设计")
picture(s, img("用例图.png"), Inches(0.4), Inches(1.2), Inches(7.4), Inches(5.7))
for i, (r, d) in enumerate([("咨询用户", "智能咨询、法条查询、文书模板、律师预约、收藏"),
                            ("律师", "资质认证、处理预约"),
                            ("管理员", "数据看板、律师审核、法条/模板/公告管理、咨询记录")]):
    y = Inches(1.5) + i * Inches(1.6)
    rect(s, Inches(8.1), y, Inches(4.8), Inches(1.35), LIGHT)
    rect(s, Inches(8.1), y, Inches(0.08), Inches(1.35), BLUE)
    text(s, Inches(8.3), y + Inches(0.08), Inches(4.5), Inches(0.5), r, 20, True, NAVY)
    text(s, Inches(8.3), y + Inches(0.6), Inches(4.5), Inches(0.75), d, 15, False, GRAY)
notes(s, "系统有三类用户：咨询用户、律师、管理员，各自的功能如右侧所示。核心是咨询用户的智能咨询。（约30秒）")

# 7 架构
s = new_slide("系统总体架构", "03 系统设计")
picture(s, img("图3-1_系统总体架构图.png"), Inches(0.4), Inches(1.2), Inches(8.2), Inches(5.8))
bullets(s, Inches(8.8), Inches(1.5), Inches(4.2), Inches(5.3), [
    "前后端分离的B/S架构",
    "浏览器 → Vue前端 → Spring Boot后端",
    "后端负责鉴权、业务数据和会话记录",
    "智能咨询请求由后端代理调用扣子API，令牌不暴露给浏览器",
    "回答以SSE流式返回，边生成边显示"], 17)
notes(s, "整体是前后端分离架构。关键设计是：智能体调用由后端代理，令牌不暴露给浏览器；回答以流式方式返回，用户两三秒就能看到第一个字。（约40秒）")

# 8 智能体
s = new_slide("法律咨询智能体设计", "04 系统实现")
picture(s, img("图3-3_法律咨询智能体结构图.png"), Inches(0.4), Inches(1.2), Inches(6.6), Inches(5.6))
text(s, Inches(7.2), Inches(1.3), Inches(5.8), Inches(0.5), "知识库", 20, True, NAVY)
bullets(s, Inches(7.2), Inches(1.85), Inches(5.8), Inches(2.0), [
    "来源：国家法律法规数据库，6部现行法律",
    "按“编-章-条”解析，一条法条一个片段，共1706条",
    "片段开头写明法律全称和条号，脚本校验条号连续"], 15)
text(s, Inches(7.2), Inches(3.9), Inches(5.8), Inches(0.5), "人设与回复逻辑", 20, True, NAVY)
bullets(s, Inches(7.2), Inches(4.45), Inches(5.8), Inches(2.4), [
    "固定结构：问题分析 / 法律依据 / 处理建议 / 风险提示",
    "只依据检索到的条文作答，查不到时如实说明",
    "非法律问题拒答，回答末尾附免责声明",
    "关闭深度思考，首字耗时从约40秒降到数秒"], 15)
notes(s, "智能体的核心是知识库和人设。知识库按条切分，每个片段带法律名和条号，单独召回也知道出处。人设规定了四段式结构、只依据检索条文作答、非法律问题拒答。联调时关闭深度思考，首字时间从约40秒降到2到3秒。（约1分钟）")

# 9 时序
s = new_slide("智能咨询流程", "04 系统实现")
picture(s, img("图3-4_智能咨询时序图.png"), Inches(0.4), Inches(1.2), Inches(8.0), Inches(5.8))
bullets(s, Inches(8.6), Inches(1.5), Inches(4.4), Inches(5.3), [
    "用户提问 → 后端校验登录、保存问题",
    "后端调用扣子流式对话接口",
    "智能体检索知识库 → 生成回答",
    "后端逐段转发给浏览器，同时拼接完整回答",
    "结束后保存回答，更新会话"], 17)
notes(s, "这是一次咨询的完整流程：后端先保存问题，再调用扣子流式接口，边收边转发，结束后把完整回答存库。（约30秒）")

# 10 界面
s = new_slide("系统界面", "04 系统实现")
shots = [("图4-4_智能咨询页面.png", "智能咨询"), ("图4-5_法条查询页面.png", "法条查询"),
         ("图4-6_律师预约页面.png", "律师预约"), ("图4-7_管理员数据看板.png", "管理员数据看板")]
for i, (f, cap) in enumerate(shots):
    x = Inches(0.5) + (i % 2) * Inches(6.25)
    y = Inches(1.2) + (i // 2) * Inches(2.95)
    picture(s, img(f), x, y, Inches(6.0), Inches(2.5))
    text(s, x, y + Inches(2.5), Inches(6.0), Inches(0.4), cap, 14, True, NAVY, PP_ALIGN.CENTER)
notes(s, "这是系统主要界面。现场我会切到系统做演示：问一个法律问题，看流式输出和法条依据；再问一个非法律问题，看拒答。（演示约2分钟；如网络不通，就用这页截图讲）")

# 11 测试概览
s = new_slide("测试结果概览", "05 系统测试")
card(s, Inches(0.6), Inches(1.4), Inches(3.9), Inches(2.3), "28 / 28", "接口功能测试用例全部通过", GREEN)
card(s, Inches(4.7), Inches(1.4), Inches(3.9), Inches(2.3), "9.14 → 0.37 秒", "50用户并发时平均首事件时间（调整线程池后）", BLUE)
card(s, Inches(8.8), Inches(1.4), Inches(3.9), Inches(2.3), "86.0%", "50道法律题的法律依据正确率（43/50）", ORANGE)
card(s, Inches(0.6), Inches(4.0), Inches(3.9), Inches(2.3), "10 / 10", "非法律问题全部拒答", GREEN)
card(s, Inches(4.7), Inches(4.0), Inches(3.9), Inches(2.3), "2.5 秒", "平均首字耗时", BLUE)
card(s, Inches(8.8), Inches(4.0), Inches(3.9), Inches(2.3), "58 / 60", "符合统一格式免责声明要求", ORANGE)
notes(s, "测试分三类。功能测试28项全部通过；性能测试发现并修正了线程池排队问题；效果测试在60题上，法律依据正确率86%，非法律问题全部拒答，平均2.5秒出第一个字。（约40秒）")

# 12 性能
s = new_slide("性能测试：发现并修正线程池排队", "05 系统测试")
rows = [["并发用户", "调整前 平均首事件", "调整后 平均首事件"], ["10", "1.06 秒", "0.37 秒"], ["20", "3.03 秒", "0.33 秒"], ["50", "9.14 秒", "0.37 秒"]]
tbl = s.shapes.add_table(4, 3, Inches(0.6), Inches(1.5), Inches(6.3), Inches(2.4)).table
for r, row in enumerate(rows):
    for c, v in enumerate(row):
        cell = tbl.cell(r, c)
        cell.text = v
        para = cell.text_frame.paragraphs[0]
        para.alignment = PP_ALIGN.CENTER
        para.runs[0].font.size, para.runs[0].font.name = Pt(16), FONT
        para.runs[0].font.bold = r == 0
        if r == 0:
            cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
            para.runs[0].font.color.rgb = WHITE
text(s, Inches(0.6), Inches(4.1), Inches(6.3), Inches(0.5), "数据来自论文表 6-4 及 6.3 节；调整后50并发完成时间为3.40秒，与单用户基本一致。", 12, False, GRAY)
text(s, Inches(7.3), Inches(1.4), Inches(5.6), Inches(0.5), "原因", 20, True, NAVY)
bullets(s, Inches(7.3), Inches(1.95), Inches(5.6), Inches(2.2), [
    "线程池核心线程8、队列100：队列不满不建新线程",
    "同一时刻只有8个回答在生成，其余排队"], 16)
text(s, Inches(7.3), Inches(4.0), Inches(5.6), Inches(0.5), "修正", 20, True, NAVY)
bullets(s, Inches(7.3), Inches(4.55), Inches(5.6), Inches(2.2), [
    "回答生成时线程主要在等网络，几乎不占CPU",
    "核心与最大线程数调为64，空闲超时回收",
    "调整后80次并发问答全部成功，28项功能测试再次通过"], 16)
notes(s, "性能测试里发现，用户越多首字越慢，50人时要9秒。原因是线程池只有8个核心线程，队列不满不会扩容，所以只有8个回答在同时生成。因为生成过程主要在等网络，我把线程数调到64，50人并发首事件时间降到0.37秒。（约1分钟）")

# 13 效果评判方法
s = new_slide("智能体效果测试方法", "05 系统测试")
bullets(s, Inches(0.6), Inches(1.4), Inches(6.2), Inches(5.2), [
    "测试集：自建60题",
    "  劳动用工、婚姻家庭、合同纠纷、消费维权、交通事故各10题",
    "  另有10道非法律问题，检验拒答",
    "每题新建会话，通过系统后端接口提问，记录全文与耗时",
    "对照组：人设、模型完全相同，但不挂知识库"], 17)
rect(s, Inches(7.1), Inches(1.4), Inches(5.7), Inches(5.2), LIGHT)
text(s, Inches(7.35), Inches(1.55), Inches(5.3), Inches(0.5), "“法律依据正确”的判定标准", 19, True, NAVY)
bullets(s, Inches(7.35), Inches(2.15), Inches(5.3), Inches(4.3), [
    "引用的每一条法条都真实存在",
    "转述内容与法条原文相符",
    "所引条文与问题相关",
    "任何一处条号错、内容错、引用不对应，或完全没引条文 → 判错",
    "脚本自动把引用条文与知识库原文并列，知识库外条文到官方网站核对原文"], 15)
notes(s, "效果测试用自建的60题，五类各10题加10道非法律题。判定标准很严格：引用的每一条都要真实存在、转述正确、与问题相关，有一处错就整题判错。脚本把回答里引用的条文和原文并排列出，知识库外的条文到最高法、政府网等官方网站核对。（约50秒）")

# 14 对照实验
s = new_slide("对照实验：知识库的作用", "05 系统测试")
picture(s, img("图5-1_各类别法律依据正确题数.png"), Inches(0.4), Inches(1.2), Inches(6.6), Inches(4.4))
rows = [["指标", "知识库组", "对照组"], ["法律依据正确", "43/50 (86.0%)", "39/50 (78.0%)"],
        ["引用知识库外规定（条数）", "21 条", "53 条"], ["引用知识库外规定（题数）", "11 题", "34 题"]]
tbl = s.shapes.add_table(4, 3, Inches(7.2), Inches(1.4), Inches(5.7), Inches(2.2)).table
for r, row in enumerate(rows):
    for c, v in enumerate(row):
        cell = tbl.cell(r, c)
        cell.text = v
        para = cell.text_frame.paragraphs[0]
        para.alignment = PP_ALIGN.CENTER
        para.runs[0].font.size, para.runs[0].font.name = Pt(14), FONT
        para.runs[0].font.bold = r == 0
        if r == 0:
            cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
            para.runs[0].font.color.rgb = WHITE
rect(s, Inches(7.2), Inches(3.9), Inches(5.7), Inches(2.9), WHITE, ORANGE)
text(s, Inches(7.4), Inches(4.0), Inches(5.3), Inches(2.8), [
    "如实看待结果：",
    "· 正确率提高8个百分点，但对结果不同的12题做符号检验，p≈0.39，差异不显著",
    "· 更明显的作用是依据可追溯：知识库外引用从53条降到21条，回答附知识库来源"], 15, False, GRAY)
notes(s, "对照实验是本文的重点。挂知识库后正确率从78%提到86%，但我做了符号检验，p约0.39，不显著，这一点我在论文里如实写了。更明显的作用是可追溯：知识库外的引用从53条降到21条，用户可以核对出处。（约1分钟）")

# 15 错误分析 & 不足
s = new_slide("错误分析与不足", "06 总结")
text(s, Inches(0.6), Inches(1.3), Inches(6), Inches(0.5), "7道错题的原因", 20, True, NAVY)
bullets(s, Inches(0.6), Inches(1.85), Inches(6), Inches(4.8), [
    "引用真实但不对应（5题）",
    "  如押金问题引用了“租赁物被查封时承租人可解除合同”",
    "转述错误（1题）",
    "  “向销售者追偿”写成“向消费者追偿”",
    "未引用条文（1题）",
    "  彩礼问题知识库未覆盖，智能体如实说明查不到"], 16)
text(s, Inches(6.9), Inches(1.3), Inches(6), Inches(0.5), "不足与改进", 20, True, NAVY)
bullets(s, Inches(6.9), Inches(1.85), Inches(6), Inches(4.8), [
    "知识库只有6部法律 → 补充行政法规、司法解释，建立更新机制",
    "人设规则不能完全阻止模型引用库外规定 → 用工作流增加条文适用性判断",
    "每类仅10题、每题问一次 → 扩大测试集，多次提问，请法律专业人员参与评判",
    "依赖扣子平台可用性 → 增加失败重试与降级提示"], 16)
notes(s, "7道错题主要是引用了真实但不对应的条文，说明检索召回的条文有时会把模型带偏。不足方面：知识库规模小、测试题量小、依赖平台。后续可以扩充知识库、用工作流做条文适用性判断、扩大测试规模。（约50秒）")

# 16 总结
s = new_slide("总结", "06 总结")
for i, t in enumerate(["从国家法律法规数据库整理6部法律1706条原文，建立知识库并校验完整性",
                       "搭建并发布法律咨询智能体，用人设约束回答结构、引用规则和拒答",
                       "开发前后端分离的Web系统，流式代理调用智能体，实现三类角色业务功能",
                       "功能28项全部通过；修正线程池问题后并发响应及时；法律依据正确率86.0%",
                       "对照实验显示知识库的主要价值在于回答依据可追溯"]):
    y = Inches(1.35) + i * Inches(1.0)
    rect(s, Inches(0.8), y, Inches(0.6), Inches(0.6), BLUE)
    text(s, Inches(0.8), y, Inches(0.6), Inches(0.6), str(i + 1), 20, True, WHITE, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    text(s, Inches(1.6), y, Inches(11), Inches(0.6), t, 19, False, RGBColor(0x33, 0x33, 0x33), anchor=MSO_ANCHOR.MIDDLE)
text(s, Inches(0.8), Inches(6.35), Inches(11.7), Inches(0.6), "恳请各位老师批评指正，谢谢！", 24, True, NAVY, PP_ALIGN.CENTER)
notes(s, "总结一下本文的五项工作（逐条念）。我的汇报到此结束，恳请各位老师批评指正，谢谢！（约40秒）")

assert page[0] == TOTAL, page[0]
prs.save(OUT)
print("已生成：", OUT, "共", page[0], "页")
