# 法律咨询助手 —— 基于Coze智能体的法律咨询系统（前端）

技术栈：Vite 5 + Vue 3（`<script setup>`）+ Vue Router 4 + Pinia + Element Plus + Axios + ECharts 5 + markdown-it。

## 环境要求

- Node.js 18+（推荐 22）
- 后端服务 `legal-consult-server` 运行在 `http://localhost:8080`

## 安装

```bash
npm install
```

## 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173 。开发环境下 `/api` 与 `/files` 请求由 Vite 代理到 `http://localhost:8080`（见 `vite.config.js`）。

初始管理员账号：`admin / admin123`（由后端初始化）。

## 构建

```bash
npm run build
```

产物输出到 `dist/`，可用 `npm run preview` 本地预览。部署时需由 Nginx 等将 `/api` 反向代理到后端，并对前端路由做 history 回退：

```nginx
location / {
  try_files $uri $uri/ /index.html;
}
location /api/ {
  proxy_pass http://127.0.0.1:8080;
  proxy_buffering off;
}
```

`proxy_buffering off` 用于保证智能咨询 SSE 流式输出实时到达浏览器。

## 目录结构

```
src/
  api/          接口封装（request.js 为 axios 实例，chat.js 为 SSE 流式请求）
  components/   公共组件
  layouts/      顶部导航布局（用户/律师）、侧边栏布局（管理员）
  router/       路由与按角色的路由守卫
  stores/       Pinia 用户状态（持久化到 localStorage）
  styles/       全局样式
  utils/        工具函数（markdown 渲染、时间格式化、常量）
  views/        页面（user / lawyer / admin / common）
```

## 角色与页面

| 角色 | 页面 |
|---|---|
| 公共 | 登录、注册（咨询用户 / 律师） |
| USER | 智能咨询、法条查询、文书模板、找律师、我的（个人信息/修改密码/我的预约/我的收藏） |
| LAWYER | 资质认证、预约处理、个人信息 |
| ADMIN | 数据看板、用户管理、律师审核、法条管理、文书模板管理、公告管理、咨询记录 |
