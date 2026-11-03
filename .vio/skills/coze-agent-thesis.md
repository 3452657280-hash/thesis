---
name: coze-agent-thesis
description: 本科毕业设计「基于Coze智能体的XX系统设计与实现」全流程经验：开题材料（文献综述/开题报告）、文献零编造核实、扣子(coze.cn)智能体+知识库搭建与API发布、Spring Boot+Vue 接入 Coze Chat v3 流式接口、法律等官方数据源知识库构建、智能体问答效果测试与论文撰写，以及实际踩过的坑。用户说「Coze智能体毕设」「扣子智能体接入系统」「做开题报告/文献综述」「智能体测试章节」时使用。
scope: local
---

# Coze 智能体类毕业设计：经验与踩坑

来源项目：`基于Coze智能体的法律咨询系统的设计与实现`（2027届 智能科学与技术）。工作区：`桌面\论文`。

## 0. 项目文件地图（复用时先看）
| 路径 | 作用 |
|---|---|
| `论文框架.md` | 论文章节框架、图表清单、与附件5/6对应关系 |
| `.vio/plans/2026-11-03_legal-consult-thesis.md` | 总体计划与进度 checklist |
| `资料/参考文献清单.md` | 每篇文献的核实状态（✅/🟡）、核实URL、可支撑论断 |
| `资料/Coze接入调研.md` | Coze 官方文档要点（鉴权、Chat v3、SSE、知识库、工作流、额度） |
| `资料/docgen.py` `gen_review.py` `gen_proposal.py` | 用 python-docx 生成综述/开题 Word（引用自动上标、自检字数与引用顺序） |
| `交付/附件5_文献综述.docx` `交付/附件6_开题报告.docx` | 交付物 |
| `智能体/人设与回复逻辑.md` `搭建步骤.md` | 智能体提示词与平台搭建步骤 |
| `智能体/fetch_laws.py` `build_kb.py` `check_kb.py` | 官方数据源下载→一条一段知识库→完整性校验 |
| `code/legal-consult-server` | Spring Boot 3 后端（mock/真实 Coze 双模式） |
| `code/legal-consult-web` | Vue3 + Element Plus 前端 |
| `code/API约定.md` `code/sql/` | 前后端接口契约、建表与法条导入脚本 |
| `测试/testset.csv` `run_eval.py` `stats.py` | 60题测试集、批量调用、统计 |

## 1. 学校要求（江西应用科技学院 智科，先读手册再动手）
- 顺序：**文献综述合格后才能开题**；开题 2026.10下旬–11下旬，答辩 2027-05-09 前。
- 综述 ≥2000 字（引言/意义/现状/问题/解决方法/总结展望/文献）；开题正文 ≥3000 字、文献 ≥10；论文约1万字，文献 ≥10 且外文 ≥2。
- 用学校附件6模板（6栏，含"可能遇到的问题及对策"），不要照抄参考报告的格式；参考模板本身有错误（混入无关文献、重复"第一部分"）。
- 老师硬性要求：近几年文献、不引 EDA/通信等不相关文献、要有智能体论文、删 DOI、句末上标引用、GB/T 7714 统一格式、段落成文不分点、不写做不到的功能、去套话。查重 >20% 不能答辩，有 AIGC 检测。
- 指导手册是 .doc：read_file 只能读到部分，用 Word COM `SaveAs2(..., 7, ... 65001)` 转 UTF-8 txt 再 grep。

## 2. 文献：零编造原则
- 每篇必须在官方页面看到原始条目才收录；`资料/参考文献清单.md` 记录核实 URL 与状态。🟡 条目定稿前须知网补全。
- 用两个并行子代理分别核实中文、外文文献最快；外文用 arxiv_search + 期刊/会议官网。
- 数字论断只用摘要原文（如 Dahl 法律幻觉"至少58%"取期刊版，arXiv 版是 58%–88%）。
- **坑**：转载页可能标错刊名。龚善要《生成式人工智能赋能公共法律服务的范式转型》实际在《东方法学》2024(5):88-，东南大学转载页误标《法学论坛》。以期刊主办方目录为准。
- **坑**：结束页码在公开网页上常查不到（王禄生、龚善要），只能知网补，不能猜。
- 公开网页找不到"Coze+法律咨询"期刊论文 → 综述里写"尚不多见"，不要写"没有"。
- 生成 Word：`docgen.py` 把 `[n]` 自动转上标，脚本末尾校验"引用首次出现顺序连续递增"和字数。

## 3. 扣子（coze.cn）平台：踩坑与正确路径
- 国内版 **www.coze.cn**；新版"扣子编程" code.coze.cn 只能对话式生成 Agent，**没有知识库/API发布入口，不要在那里建**。
- 正确入口：`https://www.coze.cn/space` 旧版后台（左侧 项目开发 / 资源库 / API管理）→ 资源库建知识库 → 项目开发 → 创建 → 智能体 → **标准创建**，模式选 **单 Agent（自主规划）**。
- bot_id = 编辑页地址栏 `bot/` 后的数字。对话式页面里的 `agentId` 不是可调用的 bot_id。
- 技能市场里的"技能"、MCP、插件（尤其联网搜索）**都不要加**：会绕过知识库、论文难解释、测试无法归因。
- 知识库：文本类型，本地文档上传；自定义分段"换行"、最大长度 800、重叠 0。**文件必须一条法条一行、条间空行**（否则多段条文会被按换行拆碎）。
- 发布必须勾选 **API（Agent As API）**；未勾选时 API 返回 HTTP 200 + JSON `code 4015 "has not been published to the channel Agent As API"`（不是 SSE！）。发布后约 30–60 秒才生效。
- 令牌：API管理 → 个人访问令牌，最长 30 天、只显示一次；名称随意（如 legal-consult-server）。
- 积分：初始 3000，每次带知识库的问答约 20–25 积分 → 先估算测试集规模；对照组用抽样（如20题）。
- 豆包 2.0 pro 带深度思考时首字约 40 秒，**关闭深度思考后首字 3.7 秒、整条 19.2 秒**（同一题实测）；换模型时平台可能报内部错误（只给 logId），重试/刷新或改为关闭思考开关。测试前务必截图确认模型名与思考开关，论文测试环境要写明。
- 开场白在"对话体验"里设置，只作用于扣子自带界面，不影响自建前端。
- "创建副本"可能报平台内部错误（只给 logId）→ 对照组改为手动标准创建，人设、模型参数逐项照抄，只去掉知识库。
- 发布按钮旁的红色"!"是平台报错提示（如创建副本失败），不代表未发布；不要据此判断发布状态。API 调用的始终是最近一次发布的版本，改完配置要重新发布。
- 对照组的开场白可照抄（API 调用不使用开场白，不影响测试）。
- 本项目正式测试配置（写入论文测试环境表）：豆包·2.0·pro、Chat Api 协议、生成多样性"精确模式"、重复语句惩罚 0、携带上下文轮数 3、最大回复长度 4096、深度思考关闭。

## 4. 后端接入 Coze（Spring Boot）
- 接口：`POST https://api.coze.cn/v3/chat?conversation_id=...`（conversation_id 在 query），body：bot_id、user_id、stream=true、auto_save_history=true、additional_messages[{role:user,content,content_type:text}]。
- SSE：`event:`/`data:` 冒号后可能无空格；增量取 `conversation.message.delta` 且 type=answer；完整答案 `conversation.message.completed` type=answer；`verbose` 中 msg_type=knowledge_recall 是知识库召回；结束 `conversation.chat.completed`/`done`；失败 `conversation.chat.failed`/`error`。
- **坑**：错误时 Coze 返回 HTTP 200 + `application/json`，必须先判 Content-Type，否则只会看到"智能体未返回有效回答"（已修复于 CozeClient）。
- **坑（企业网络）**：Windows curl 报 `CRYPT_E_NO_REVOCATION_CHECK`，JVM 报 `PKIX path building failed`。解决：启动加 `-Djavax.net.ssl.trustStoreType=Windows-ROOT`。
- 令牌不得进 jar：`application-local.yml` 放在**运行目录**（`code/legal-consult-server/`），通过 `spring.config.import: optional:file:./application-local.yml` 读取，并在 .gitignore 忽略；打包后检查 jar 内无该文件。
- 默认 mock 模式（无 token 自动 mock），便于未建好智能体时联调；mock 冒烟数据测完即删，不得混入正式结果。
- 回答末尾 [1][2] 来源链接是扣子临时签名 URL，会过期 → 论文截图要趁早。

## 5. 知识库数据（以法律为例）
- 只用官方源：国家法律法规数据库 flk.npc.gov.cn。旧 API 已失效（405）；新接口从前端 bundle 逆向：
  - `POST /law-search/search/list`，body 需含 `orderByParam:{order:"-1",sort:""}`、searchContent、pageNum、pageSize；
  - 结果过滤：标题去 `<em>` 后完全等于法律名、`sxx==3`（有效），按 gbrq 取最新；
  - `GET /law-search/download/pc?format=docx&bbbs=...&fileId=` 返回 data.url 再下载。
- `build_kb.py` 解析"第X编/章/条"，每段开头带《法律名》第X条（编·章）；`check_kb.py` 用中文数字转换校验条号连续。6部法律共1706条，最长 665 字。
- 施行日期写入 `_来源记录.json` 并同步到 law_article.effective_date 与论文表3-1。

## 6. 测试与评判（第5章）
- 测试集：5类法律各10题 + 非法律10题；expected_law/articles 只能取自知识库原文，无依据标"知识库未覆盖"（本项目4题：工伤认定、彩礼返还、无证驾驶保险、伤残鉴定）。
- `run_eval.py` 走系统后端（端到端），每题新会话；结果 CSV 留人工评判列；`stats.py` 计算法律依据正确率、拒答率、首字/总耗时 P90。
- 评判"法律依据正确"要严格：条号真实 + 内容与原文相符 + 相关；模型把概括写成引文（如在第四十七条前加"因欠薪解除合同的"）记为不严谨。
- 典型错误：漏掉条文例外（劳动争议调解仲裁法第二十七条：劳动关系存续期间追讨欠薪不受一年时效限制）→ 人设中加"引用须完整阅读条文、不得遗漏但是/除外"。这类"发现问题→优化人设"可写进论文。
- 联调与速度复测记录放 `测试/联调记录/`，与正式结果分开。

## 7. 协作经验
- 用户会说"其他你自己做"：凡能自动化的（下载数据、标注、编译、联调）都自己做；只有注册账号、平台点选、令牌这类必须本人操作的才交给用户，并给出逐步截图式指引。
- 用户给截图时，逐项核对（召回卡片的条文与知识库原文比对），发现自己之前判断错了要明确纠正。
- 并行子代理适合：中外文文献核实、前后端分别开发、测试集标注；每个子代理限定可写目录，事后自己抽查。
- Windows 下 `python -c` 不支持 `\n` 多行，写成临时脚本；cmd 中文路径输出乱码不代表失败。

## 8. 测试与论文生成（补充经验）
- run_eval.py 在后台跑时 stdout 有缓冲，看起来"卡住"其实在跑 → 设 `PYTHONUNBUFFERED=1`，或直接看结果 CSV 行数。
- 对照组不必改主配置：另起一个实例 `java -jar ... --server.port=8081 --coze.bot-id=<对照bot>`，命令行参数覆盖 application-local.yml。
- 功能测试用 `测试/func_test.py` 在 mock 实例（`--coze.mock=true --server.port=8082`）上跑 28 个接口用例，不耗积分，结果写 CSV。
- 评判：`make_judge_packet.py` 把回答里每条"《法》第X条"与知识库原文对齐生成评判材料 → 子代理分段评判（知识库外条文到 court.gov.cn / gov.cn 核实）→ `merge_judge.py` 合并统计。子代理之间结论冲突要亲自复核（例：公安部令146号全文在 gd.gov.cn 可取，mps.gov.cn 常 521）。
- 实测结论（写论文用）：知识库组 50 道法律题依据正确 43/50=86.0%；同 20 题 知识库 19/20 vs 对照 18/20，差异不显著，但外部条文引用 9 条 vs 19 条 → 论文重点写"依据可追溯"，不要夸大正确率提升。
- 论文生成：`资料/thesis_content.py`（正文数据）+ `thesis_figs.py`（Pillow 画图，无 matplotlib）+ `gen_thesis.py`（按学校撰写规范排版，自检引用顺序/字数）。
- **坑**：用公司电脑的 Word COM 打开并保存会自动加敏感度标签，页脚出现 "Internal" → 交付文件不要用 Word COM 保存；目录留域代码，让用户打开后按 F9 更新。Word COM 进程卡住时用 `$w.DisplayAlerts=0`，并清理残留 WINWORD 进程。

## 9. 当前进度（2026-11-03）
- 已完成：综述、开题、知识库、前后端、联调、主测试60题、对照组20题、人工评判、功能测试28项、论文初稿（交付/毕业论文_*.docx，正文约1.5万字，21篇文献/外文7篇）。积分剩余约 1000+。
- 待办（需用户）：论文中黄色标注处插入系统与扣子平台截图；封面/声明等学校模板页；🟡文献（王禄生、龚善要页码，银莉卷期页）知网补全；导师审阅。

