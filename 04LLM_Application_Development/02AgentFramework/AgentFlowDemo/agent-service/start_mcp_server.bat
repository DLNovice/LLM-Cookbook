@echo off
REM MCP Server 启动脚本 (Windows)

cd /d "%~dp0"

echo 🚀 Starting MCP Demo Server...
echo Server will run on: http://localhost:8006/mcp_demo
echo.

REM 激活虚拟环境（如果存在）
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM 启动 MCP Server
python -m src.tools.shttp_demo_server

pause
