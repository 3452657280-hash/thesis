@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo [1/2] 启动后端（端口 8080）...
start "法律咨询-后端" cmd /k "cd /d legal-consult-server && java -Djavax.net.ssl.trustStoreType=Windows-ROOT -jar target\legal-consult-server.jar"

echo [2/2] 启动前端（端口 5173）...
if not exist "legal-consult-web\node_modules" (
  echo 首次运行，正在安装前端依赖...
  start "法律咨询-前端" cmd /k "cd /d legal-consult-web && npm install && npm run dev"
) else (
  start "法律咨询-前端" cmd /k "cd /d legal-consult-web && npm run dev"
)

echo 等待服务启动...
timeout /t 25 /nobreak >nul
start http://localhost:5173
echo 已打开浏览器。关闭两个黑色窗口即可停止系统。
