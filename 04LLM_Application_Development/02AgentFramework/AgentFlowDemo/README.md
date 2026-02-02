# Agent 聊天系统 (AgentFlowDemo)

一个完整的 Agent 聊天系统，包含 LangGraph Agent 服务、Golang 后端和 Vue.js 前端。

## 系统架构

```
┌─────────────┐      WebSocket       ┌──────────────┐      HTTP/SSE      ┌─────────────────┐
│             │ ◄──────────────────► │              │ ◄────────────────► │                 │
│  Vue.js     │                      │   Golang     │                    │  Python Agent   │
│  Frontend   │                      │   Backend    │                    │  (LangGraph)    │
│             │                      │   (Gin)      │                    │                 │
└─────────────┘                      └──────────────┘                    └─────────────────┘
                                            │                                     │
                                            │                                     │
                                            ▼                                     ▼
                                      Session 管理                          MCP 工具集成
```

## 目录结构

```
AgentFlowDemo/
├── agent-service/          # Python LangGraph Agent 服务
│   ├── src/
│   │   ├── agent/         # Agent 核心逻辑
│   │   ├── api/           # FastAPI 接口
│   │   ├── tools/         # MCP 工具集成
│   │   └── utils/         # 工具函数
│   ├── pyproject.toml     # uv 项目配置
│   └── .env.example       # 环境变量模板
│
├── backend/               # Golang 后端服务
│   ├── cmd/              # 主程序入口
│   ├── internal/         # 内部实现
│   │   ├── handler/      # HTTP/WebSocket 处理器
│   │   ├── service/      # 业务逻辑
│   │   └── model/        # 数据模型
│   ├── go.mod
│   └── .env.example
│
├── frontend/             # Vue.js 前端
│   ├── src/
│   │   ├── components/   # Vue 组件
│   │   ├── views/        # 页面视图
│   │   └── services/     # API/WebSocket 服务
│   ├── package.json
│   └── vite.config.js
│
└── README.md            # 本文件
```

## 快速开始

### 0. 启动 MCP Server (可选但推荐)

**如果您想使用 MCP 工具功能，需要先启动 MCP Server:**

```bash
cd agent-service

# Linux/macOS:
./start_mcp_server.sh

# Windows:
# start_mcp_server.bat

# 或者手动启动:
python -m src.tools.shttp_demo_server
```

MCP Server 将运行在 `http://localhost:8006/mcp_demo`

### 1. 启动 Agent 服务 (Python)

```bash
cd agent-service
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .
cp .env.example .env
# 编辑 .env 设置 OPENROUTER_API_KEY
python -m uvicorn src.api.main:app --reload --port 8000
```

### 2. 启动 Golang 后端

```bash
cd backend
cp .env.example .env
go mod download
go run cmd/main.go
# 默认运行在 :8080
```

### 3. 启动 Vue 前端

```bash
cd frontend
npm install
npm run dev
# 默认运行在 http://localhost:5173
```

## 功能特性

### Agent 服务
- ✅ 基于 LangGraph 的工作流引擎
- ✅ 智能意图识别和工具调用
- ✅ **MCP 工具集成支持**（可调用外部 MCP Server 工具）
- ✅ 内置天气查询工具
- ✅ SSE 流式输出

### MCP 工具集成
- ✅ 支持 FastMCP 的 streamable-http 协议
- ✅ 自动发现和加载 MCP 工具
- ✅ 智能工具选择和参数提取
- ✅ 示例工具：add (数学计算)、get_weather (天气查询)
- ✅ 易于扩展，支持自定义工具

### 后端服务
- ✅ Gin Web 框架
- ✅ WebSocket 实时通信
- ✅ 多用户会话管理
- ✅ 端到端流式传输

### 前端界面
- ✅ Vue 3 + Vite
- ✅ 实时聊天界面
- ✅ 流式消息渲染
- ✅ 响应式设计

## API 文档

### 后端 API

- `POST /api/chat/send` - 发送消息
- `GET /api/chat/ws` - WebSocket 连接

### Agent API

- `POST /agent/chat` - 普通对话
- `GET /agent/stream` - SSE 流式对话

## 技术栈

- **Agent**: Python 3.11+, LangGraph, FastAPI, FastMCP
- **Backend**: Golang 1.21+, Gin, Gorilla WebSocket
- **Frontend**: Vue 3, Vite, TypeScript

## 📚 文档

- [MCP 集成文档](agent-service/MCP_INTEGRATION.md) - MCP Server 集成详细说明
- [部署指南](DEPLOYMENT.md) - 完整部署和配置文档
- [快速启动](QUICKSTART.md) - 快速启动脚本和测试方法

## License

MIT
