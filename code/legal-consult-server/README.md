# legal-consult-server

基于 Coze 智能体的法律咨询系统后端（Spring Boot 3.3 + MyBatis-Plus + Spring Security/JWT）。接口契约见 `../API约定.md`。

## 环境

- JDK 17
- 无需本机安装 Maven，使用项目自带的 Maven Wrapper（`mvnw.cmd` / `mvnw`）

## 运行方式

### 1. dev（默认，H2 内存库）

```powershell
cd code\legal-consult-server
.\mvnw.cmd -DskipTests package
java -jar target\legal-consult-server.jar
```

- 默认 profile 为 `dev`，H2 内存库（MODE=MySQL），启动时执行 `db/schema-h2.sql`、`db/data-h2.sql`、`db/data-laws.sql`（6部法律共1706条原文），重启后数据清空。
- 服务端口 8080，前端开发服务器 `http://localhost:5173` 已加入 CORS 白名单。

### 2. mysql

1. 执行 `code/sql/schema.sql` 建库建表（库名 `legal_consult`）。
2. 启动：

```powershell
$env:DB_USERNAME="root"; $env:DB_PASSWORD="root"   # 可选，默认均为 root
java -jar target\legal-consult-server.jar --spring.profiles.active=mysql
```

可选环境变量：`DB_HOST`（默认 localhost）、`DB_PORT`（默认 3306）、`JWT_SECRET`。
mysql profile 不执行初始化 SQL，首次启动只会自动创建管理员账号。法条数据：执行 `code/sql/law_article_data.sql`（由 `智能体/build_kb.py` 从国家法律法规数据库原文生成）。

## Coze 配置

默认 `coze.mock=true`（演示模式）：不访问网络，返回带“【演示模式：未连接Coze智能体】”前缀的示例回答，启动日志会给出 WARN 提示。token 或 bot-id 为空时同样自动进入演示模式。

接入真实智能体，二选一：

**环境变量**

```powershell
$env:COZE_TOKEN="pat_或sat_令牌"
$env:COZE_BOT_ID="智能体ID"
$env:COZE_MOCK="false"
java -jar target\legal-consult-server.jar
```

**application-local.yml**（已在 .gitignore 中忽略，可放在 `src/main/resources/` 或运行目录）

```yaml
coze:
  token: pat_xxx
  bot-id: "7xxxxxxxxxxxxxxxxxx"
  mock: false
```

其他配置：`coze.base-url`（默认 https://api.coze.cn）、`coze.timeout-seconds`（默认 120）。

**企业网络 / HTTPS 证书报错**：若出现 `PKIX path building failed`（公司网络做了 HTTPS 代理），启动时加 `-Djavax.net.ssl.trustStoreType=Windows-ROOT`，让 JVM 使用 Windows 系统证书库：

```powershell
java -Djavax.net.ssl.trustStoreType=Windows-ROOT -jar target\legal-consult-server.jar
```

## 默认账号

| 账号 | 密码 | 角色 | 说明 |
|---|---|---|---|
| admin | admin123 | ADMIN | 所有 profile，库中无管理员时自动创建 |
| user1 | 123456 | USER | 仅 dev |
| lawyer1 | 123456 | LAWYER | 仅 dev，附带已审核通过的演示资质 |

管理端“重置密码”会将密码重置为 `123456`。

## 演示数据说明

法条为国家法律法规数据库（flk.npc.gov.cn）下载的现行有效原文；文书模板的下载地址为 `https://example.com` 占位链接，正式使用前请替换为真实文件。
