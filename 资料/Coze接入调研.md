# Coze（扣子）接入调研结论

> 调研日期：2026-11-03。来源为官方文档可读版 docs.coze.cn（入口 https://www.coze.cn/llms.txt）。标"待实测"的条目在开发时必须验证后才能写进论文。

## ⚠️ 两个影响全局的风险

1. **低代码智能体对新用户关闭**：文档写明"由于产品方向调整，扣子开发平台（低代码）不再向新注册用户开放。如需开发智能体、工作流、应用等，请前往扣子编程"（https://docs.coze.cn/guides_create_knowledge.md）。
   → 必须先用你的账号确认：能否创建"智能体 + 知识库 + 工作流"。若不能，技术路线改为"扣子编程"中的对应能力，论文中的平台描述随之调整。
2. **个人免费版累计仅 500 次 API 调用**，用完后该账号无法再调用任何扣子 API（https://docs.coze.cn/developer_guides_coze_api_overview.md）。
   → 开发调试尽量在扣子平台内"调试"窗口完成；后端联调控制次数；第5章智能体测试集规模定为 60 题左右并一次性批量跑；必要时开通付费版或另开账号。

## 鉴权

- 请求头：`Authorization: Bearer <token>`。
- PAT：有效期 1~30 天，不可永久，令牌只显示一次；个人版最多 10 个。
- 服务访问令牌 SAT 可设永久，适合后端服务 → 优先尝试 SAT。
- 所需权限：`chat`（/v3/chat）、`createConversation`（/v1/conversation/create）、`getChat`、`listMessage`。
- 令牌只写在后端配置/环境变量，**前端不接触令牌**。

## 发布

智能体编排页 → 发布 → 选择发布平台中勾选 **API** → 发布（需先创建令牌）。bot_id 取开发页 URL 中 `bot/` 后的数字。未发布时使用 `publish_status=unpublished_draft` 是否可调用：待实测。

## 对话接口（本系统采用）

- `POST https://api.coze.cn/v3/chat?conversation_id=<id>`（conversation_id 在 **query**）。
- Body：`bot_id`、`user_id`（建议用"系统前缀+用户ID哈希"，不直接暴露业务ID）、`stream: true`、`auto_save_history: true`、`additional_messages: [{"role":"user","content":"...","content_type":"text"}]`。
- 同一会话同时只能有一个进行中的对话（否则错误码 4016）→ 后端对同一会话加锁/前端发送中禁用输入框。
- 多轮：首次调用不传 conversation_id，从返回事件 `data.conversation_id` 取得并存入 `consult_session.coze_conversation_id`，之后每次带上。

## SSE 解析规则

- 事件格式：`event:xxx` / `data:{...}`（冒号后可能无空格，需兼容）。
- 增量文本：`conversation.message.delta` 且 `type=answer`、`role=assistant` → 取 `data.content` 追加。
- 完整答案：`conversation.message.completed` 且 `type=answer` → `data.content`。
- 结束：`conversation.chat.completed`（含 usage）或 `done`；失败：`conversation.chat.failed` / `error`。
- 忽略：`verbose`、`knowledge`、`function_call`、`tool_response`、`follow_up`。`verbose` 中 `msg_type=knowledge_recall` 可用于统计是否命中知识库（待实测）。

## 智能体能力（设计依据）

- 知识库：文本（本地文档，按层级分段支持 PDF/MD/DOC/DOCX）、表格（Excel/CSV，指定索引列）；单分段 ≤5000 字符；免费版容量 1GB。召回：混合/语义/全文检索，最大召回数、最小匹配度、无召回回复话术、显示来源。
- 工作流节点：开始（input）、意图识别（极速模式 ≤10 个意图，输出 classificationId、reason）、知识库检索（默认召回5条、最小匹配度0.5，输出 outputList）、选择器、大模型（系统/用户提示词，默认超时180s）、结束（返回变量/返回文本，支持流式）。
- 绑定：工作流需先发布 → 智能体编排页添加 → 在"人设与回复逻辑"中写明何时调用。
- 时限：Chat API 下工作流同步执行；用户提问到回复最长 2 分钟。
