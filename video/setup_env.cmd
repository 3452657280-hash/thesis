@echo off
rem 在 video\ 目录下建一个专用 Python 环境 .venv，并装好配音依赖。只需运行一次。
cd /d "%~dp0"
if exist .venv\Scripts\python.exe goto deps
where py >nul 2>nul && (py -3 -m venv .venv) || (python -m venv .venv)
:deps
.venv\Scripts\python.exe -m pip install -r requirements.txt
echo.
echo 完成。以后用  .venv\Scripts\python.exe motion_prep.py ...  运行。
