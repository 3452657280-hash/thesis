# 前后端接口约定（v1）

- 后端端口 8080，统一前缀 `/api`；前端开发服务器 5173，Vite 代理 `/api` → `http://localhost:8080`。
- 统一响应：`{ "code": 200, "msg": "success", "data": ... }`。业务错误时 code ≠ 200，并在 msg 中返回中文提示。未登录返回 HTTP 401，权限不足返回 HTTP 403。
- 鉴权：请求头 `Authorization: Bearer <jwt>`。JWT 载荷包含 `uid`、`role`，有效期 24 小时。
- 角色：`USER` / `LAWYER` / `ADMIN`。路径规则：
  - `/api/admin/**` 只允许 ADMIN；
  - `/api/lawyer/**` 只允许 LAWYER；
  - `/api/auth/**` 以及 GET 方式的 `/api/public/**` 不需要登录；
  - 其余接口登录后即可访问。
- 分页参数：`page`（从 1 开始）、`size`。分页返回：`{ "records": [], "total": n }`。

## 认证
| 方法 | 路径 | 请求 | 返回 data |
|---|---|---|---|
| POST | /api/auth/register | {username, password, nickname, phone, role: USER\|LAWYER} | null |
| POST | /api/auth/login | {username, password} | {token, user:{id,username,nickname,role}} |
| GET | /api/user/me | - | 用户信息 |
| PUT | /api/user/me | {nickname, phone, email} | null |
| PUT | /api/user/password | {oldPassword, newPassword} | null |

## 智能咨询
| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /api/consult/sessions | 当前用户的会话列表，按 update_time 倒序 |
| POST | /api/consult/sessions | 新建会话 → 返回 {id, title} |
| PUT | /api/consult/sessions/{id} | {title} 重命名会话 |
| DELETE | /api/consult/sessions/{id} | 删除会话（级联删除消息） |
| GET | /api/consult/sessions/{id}/messages | 消息列表，按时间正序 |
| POST | /api/consult/sessions/{id}/chat | 请求体 {content}；返回 `text/event-stream`，事件见下 |

SSE 事件（后端发给前端，data 均为 JSON）：
- `event: delta` → `data: {"content":"增量文本"}`
- `event: done` → `data: {"messageId":123,"userMessageId":122,"responseMs":5300,"firstTokenMs":900}`
- `event: error` → `data: {"msg":"错误说明"}`

由于 SSE 请求需要携带 JWT 请求头，前端用 `fetch` + `ReadableStream` 解析，不使用 EventSource。会话首次提问时，后端用问题的前 20 个字自动生成会话标题。

## 收藏与评价
| POST | /api/consult/messages/{id}/favorite | 收藏（重复收藏时直接忽略） |
| DELETE | /api/consult/messages/{id}/favorite | 取消收藏 |
| GET | /api/consult/favorites | 收藏列表：{messageId, content, sessionId, createTime} |
| POST | /api/consult/messages/{id}/feedback | {score:1-5, comment} |

## 法条与模板（公开）
| GET | /api/public/laws?keyword=&lawName=&page=&size= | 法条分页 |
| GET | /api/public/laws/names | 法律名称列表 |
| GET | /api/public/templates?category=&page=&size= | 文书模板分页 |
| GET | /api/public/templates/{id}/download | 下载次数 +1，并重定向到 file_url |
| GET | /api/public/notices | 公告列表 |
| GET | /api/public/lawyers?specialty=&page=&size= | 审核通过的律师列表 |

## 律师预约（用户）
| POST | /api/appointments | {lawyerId, question, appointTime} |
| GET | /api/appointments/my | 我的预约列表（含律师姓名） |

## 律师端
| GET | /api/lawyer/profile | 我的资质信息（可能为空） |
| POST | /api/lawyer/profile | {realName, licenseNo, lawFirm, specialty, years, intro}，提交或修改，提交后 audit_status 置为 0 |
| GET | /api/lawyer/appointments?status= | 我收到的预约 |
| PUT | /api/lawyer/appointments/{id} | {status:1\|2\|3, reply} |

## 管理端
| GET | /api/admin/users?keyword=&role=&page=&size= | 用户分页 |
| PUT | /api/admin/users/{id}/status | {status:0\|1} |
| PUT | /api/admin/users/{id}/reset-password | 重置为 123456 |
| GET | /api/admin/lawyers?auditStatus= | 律师资质列表 |
| PUT | /api/admin/lawyers/{id}/audit | {auditStatus:1\|2, auditRemark} |
| GET/POST/PUT/DELETE | /api/admin/laws[/{id}] | 法条增删改查 |
| GET/POST/PUT/DELETE | /api/admin/templates[/{id}] | 模板增删改查（file_url 填外链或 /files/ 路径） |
| GET/POST/PUT/DELETE | /api/admin/notices[/{id}] | 公告增删改查 |
| GET | /api/admin/consults?page=&size= | 全部问答记录（用户名、问题、回答摘要、耗时、评分） |
| GET | /api/admin/stats | {userCount, lawyerCount, sessionCount, questionCount, avgScore, avgResponseMs, dailyQuestions:[{date,count}] 近 14 天, scoreDistribution:[{score,count}]} |
