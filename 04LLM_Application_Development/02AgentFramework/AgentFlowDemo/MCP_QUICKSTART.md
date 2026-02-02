# 🚀 MCP 集成快速启动指南

## 前提条件

确保已安装：
- Python 3.11+
- uv (Python 包管理器)
- Golang 1.21+
- Node.js 18+

## 一键启动所有服务

### 步骤 1: 安装依赖

```bash
# 1. Agent 服务依赖
cd agent-service
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .

# 2. Golang 后端依赖
cd ../backend
go mod download

# 3. Vue 前端依赖
cd ../frontend
npm install
```

### 步骤 2: 配置环境变量

```bash
# Agent 服务
cd agent-service
cp .env.example .env

# 编辑 .env，设置 OpenRouter API Key
# OPENROUTER_API_KEY=sk-or-v1-xxxxx
# MCP_SERVER_URL=http://localhost:8006/mcp_demo

# Backend
cd ../backend
cp .env.example .env

# Frontend 已配置好，无需修改
```

### 步骤 3: 启动服务（需要 4 个终端）

#### 终端 1: MCP Server
```bash
cd agent-service
source .venv/bin/activate

# 使用脚本启动
./start_mcp_server.sh

# 或手动启动
python -m src.tools.shttp_demo_server
```

**预期输出**:
```
INFO:     Uvicorn running on http://0.0.0.0:8006 (Press CTRL+C to quit)
```

#### 终端 2: Agent 服务
```bash
cd agent-service
source .venv/bin/activate

python -m uvicorn src.api.main:app --reload --port 8000
```

**预期输出**:
```
INFO - Initializing MCP Enhanced Agent...
INFO - Connecting to MCP server: http://localhost:8006/mcp_demo
INFO - Loaded 2 MCP tools
INFO - MCP Enhanced Agent initialized successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 终端 3: Golang 后端
```bash
cd backend
go run cmd/main.go
```

**预期输出**:
```
Starting Agent Flow Backend Server...
Agent Service URL: http://localhost:8000
Server Port: 8080
Server starting on :8080
```

#### 终端 4: Vue 前端
```bash
cd frontend
npm run dev
```

**预期输出**:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

## 验证集成

### 1. 运行测试脚本

```bash
# 在项目根目录
./test_mcp_integration.sh
```

**预期输出**:
```
🧪 MCP Integration Test Suite
==============================

Step 1: Testing MCP Server
----------------------------
Testing: MCP Server Health ... ✓ PASSED

Step 2: Testing Agent Service
----------------------------
Testing: Agent Health Check ... ✓ PASSED
Testing: Agent Root Endpoint ... ✓ PASSED

Step 3: Testing MCP Tool Calls
----------------------------
Testing: MCP Tool: add(5, 3) ... ✓ PASSED
Testing: MCP Tool: get_weather ... ✓ PASSED

✓ All tests passed!
```

### 2. 手动测试 MCP 工具

#### 测试 add 工具

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "帮我计算 25 + 17",
    "session_id": "test1"
  }'
```

**预期响应**:
```json
{
  "response": "25 加 17 等于 42。",
  "session_id": "test1"
}
```

#### 测试 get_weather 工具

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "New York 的天气怎么样？",
    "session_id": "test2"
  }'
```

### 3. 通过前端界面测试

1. 打开浏览器访问 http://localhost:5173
2. 等待连接状态显示 "已连接"
3. 输入测试消息：

**测试用例 1 - 数学计算**:
```
输入: 帮我算一下 100 + 234
预期: Agent 调用 add 工具并返回结果 334
```

**测试用例 2 - 天气查询**:
```
输入: New York 的天气如何？
预期: Agent 调用 get_weather 工具并返回 "It's always sunny in New York"
```

**测试用例 3 - 普通对话**:
```
输入: 你好，介绍一下你自己
预期: Agent 直接回复，不调用工具
```

## 常见问题

### Q1: MCP Server 启动失败

**错误**: `Address already in use`

**解决**:
```bash
# 查找占用 8006 端口的进程
lsof -i :8006
# 或
netstat -tuln | grep 8006

# 杀死进程或修改端口
```

### Q2: Agent 无法连接 MCP Server

**错误**: `Failed to load MCP tools: Connection refused`

**检查清单**:
1. ✅ MCP Server 是否运行？
2. ✅ 端口 8006 是否正确？
3. ✅ `.env` 中 `MCP_SERVER_URL` 是否正确？

**测试连接**:
```bash
curl -X POST http://localhost:8006/mcp_demo \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

### Q3: Agent 没有调用 MCP 工具

**可能原因**:
1. LLM 没有识别到需要使用工具
2. 工具描述不够清晰

**解决方案**:
- 使用更明确的指令，如："使用 add 工具计算..."
- 查看 Agent 日志，检查意图分析结果

### Q4: OpenRouter API Key 未配置

**错误**: `OPENROUTER_API_KEY not set`

**解决**:
```bash
# 编辑 agent-service/.env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

## 查看日志

### Agent 服务日志
```bash
# 查看 MCP 工具加载
grep "Loaded.*MCP tools" agent-service.log

# 查看工具调用
grep "Calling MCP tool" agent-service.log
```

### MCP Server 日志
```bash
# 查看请求
grep "POST /mcp_demo" mcp-server.log
```

## 下一步

✅ 集成完成后，您可以：

1. **添加自定义工具** - 编辑 `shttp_demo_server.py`
2. **优化意图识别** - 调整 Agent prompt
3. **连接真实服务** - 替换 demo 工具为实际 API
4. **部署到生产** - 参考 [DEPLOYMENT.md](DEPLOYMENT.md)

## 架构图

```
┌──────────────┐
│   用户输入    │ "帮我计算 5 + 3"
└──────┬───────┘
       │
       v
┌──────────────────────────────────────────────────┐
│           Vue Frontend (localhost:5173)          │
│  - WebSocket 连接                                 │
│  - 实时显示消息                                    │
└──────────────────┬───────────────────────────────┘
                   │ WebSocket
                   v
┌──────────────────────────────────────────────────┐
│        Golang Backend (localhost:8080)           │
│  - WebSocket Handler                             │
│  - 转发到 Agent Service                          │
└──────────────────┬───────────────────────────────┘
                   │ HTTP/SSE
                   v
┌──────────────────────────────────────────────────┐
│      Agent Service (localhost:8000)              │
│  1. 分析意图: "需要调用 add 工具"                  │
│  2. 提取参数: {a: 5, b: 3}                       │
│  3. 调用 MCP Client                              │
└──────────────────┬───────────────────────────────┘
                   │ JSONRPC 2.0
                   v
┌──────────────────────────────────────────────────┐
│      MCP Server (localhost:8006)                 │
│  @mcp.tool()                                     │
│  def add(a: int, b: int) -> int:                 │
│      return a + b                                │
│                                                  │
│  返回: 8                                          │
└──────────────────┬───────────────────────────────┘
                   │
                   v
            Agent 生成响应
               "5 + 3 = 8"
                   │
                   v
          返回给用户 (流式输出)
```

## 成功标志

当您看到以下内容时，说明集成成功：

✅ MCP Server 运行在 8006 端口
✅ Agent 服务日志显示 "Loaded 2 MCP tools"
✅ 前端界面显示 "已连接"
✅ 测试脚本全部通过
✅ 可以通过聊天调用 add 和 get_weather 工具

**恭喜！您已成功集成 MCP Server！** 🎉
