#!/bin/bash
# MCP Server 启动脚本

cd "$(dirname "$0")"

echo "🚀 Starting MCP Demo Server..."
echo "Server will run on: http://localhost:8006/mcp_demo"
echo ""

# 激活虚拟环境（如果存在）
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# 启动 MCP Server
python -m src.tools.shttp_demo_server

# 注意：Ctrl+C 停止服务器
