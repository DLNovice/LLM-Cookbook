> 前要：Github上搜索`langchain golang`与`langgraph golang`与`fastapi grpc golang`，暂时没找到合适的参考项目。

此项目可拆解为三个部分：

- Golang 负责高性能 API/WebSocket 服务
- Python/LangGraph 服务负责复杂的 Agent 编排逻辑
- Vue.js 负责用户交互

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



TODO：

- MCP相关：是继续基于源码，还是重构一下，基于FastMCP封装？
- 多用户相关：加入多用户相关配置



### 设计大纲

------

Agent 核心逻辑 (Python/LangGraph)

1. 定义 Agent 图： 使用 LangGraph 定义你的 Agent 工作流（例如：用户输入 →路由 →工具调用 →LLM 反馈 →结束）。
2. 构建 LangChain Runnable： 将 LangGraph 的图编译成一个可运行的 `Runnable` 对象。
3. 创建 API Service： 使用 FastAPI 或 Flask 搭建一个轻量级的 Python Web 服务，暴露一个 POST 或 WebSocket 接口，用于接收 Golang 后端的消息，运行 LangGraph `Runnable`，并将结果返回。



后端 API/消息网关 (Golang)

- Web 服务： 使用 Gin 或 Echo 框架搭建 RESTful API 和 WebSocket 服务。
- WebSocket 实现：
  - 作用： 实现 Agent 结果的流式传输 (Streaming)，提供更好的用户体验。
  - 流程： 用户发送消息 → Golang接收 → Golang 通过 HTTP/gRPC 调用 Python/LangGraph 服务 → LangGraph 服务将结果流式返回给 Golang  → Golang 立即通过 WebSocket 将数据转发给 Vue.js 前端。
- 服务间通信： 建议使用 gRPC 进行 Golang 和 Python 服务之间的通信，因为它支持更好的流式传输和结构化消息定义（Protobuf）。



前端界面 (Vue.js)

1. 聊天组件： 实现一个可滚动的聊天组件，展示用户和 Agent 的消息。
2. WebSocket 连接： 在组件挂载时建立与 Golang 后端的 WebSocket 连接。
3. 消息处理： 监听 WebSocket 接收到的流式数据，并实时更新聊天气泡中的内容，实现类似“打字机”的效果。
4. Markdown 渲染： 使用 `marked.js` 或类似库将 Agent 返回的 Markdown 格式文本渲染成美观的 HTML。

------

示例：

```
<角色定位>
你是一位拥有多年一线实战经验的 **资深 Agent 系统架构师与全栈开发专家**，精通以下领域：
- LangGraph、Python Agent 工作流
- Golang 后端（Gin、WebSocket、gRPC/HTTP 通信）
- Vue.js 前端（组件化、聊天界面、实时流式渲染）
   你的任务是根据需求，输出结构化、可落地、可运行的工程级方案与代码。
</角色定位>

<任务描述>
我需要构建一个完整的 **Agent 聊天系统**，包括 Agent 服务（Python/LangGraph）、后端（Golang）和前端（Vue.js）。
 所有代码都需要组织在目录：
 `/home/user/WorkSpace/SimBotProject/AgentFlowDemo`
 你需要提供清晰的目录组织结构与对应代码示例。
</任务描述>

<功能需求>

### **1. Agent 核心逻辑（Python / LangGraph）**

- 使用 **LangGraph** 定义一个可运行的 Agent 工作流，可基于OpenRouter接入LangGraph提供模型服务
- Agent 功能：**简易天气查询助手**
- 支持接入 **MCP 工具（我会自己提供，不需要你生成 MCP server 代码）**
- 提供一个可被 Golang 调用的接口（HTTP 或 gRPC）
- 支持 **流式输出**（SSE 或 chunked streaming）

------

### **2. 后端服务（Golang / Gin）**

功能目标：

#### 🖥 API 服务

- 使用 **Gin** 构建 RESTful API
- 路由示例：
  - `POST /api/chat/send`：用户发送消息（调用 Python Agent 服务）
  - `GET /api/chat/stream`：WebSocket 通道，实时返回 Agent 响应

#### 🔄 与 Python 服务通信

- Golang 通过 **HTTP 或 gRPC** 调用 LangGraph 服务
- 支持 LangGraph → Golang → WebSocket → Vue 的 **端到端流式传输**

#### 👤 多用户支持

- 使用 sessionId / userId 区分对话
- WebSocket 按会话推送数据

------

### **3. 前端界面（Vue.js）**

构建一个简洁的聊天 UI：

- 使用 Vue3 + Vite
- 聊天窗口可滚动
- 左右气泡显示用户 / Agent 消息
- WebSocket 实时接收流式消息
- 输入框 + 发送按钮

</功能需求>

<输出要求>
你需要提供：
1. **目录结构设计**
2. **Agent（Python/LangGraph）核心代码，可基于uv创建Python虚拟环境**
3. **Golang 后端完整代码（含 WebSocket 实现）**
4. **Vue 前端聊天界面代码**
5. **服务之间如何联调的说明**
6. **部署与运行说明**
</输出要求>
```



### 环境配置

环境配置：首先编辑`.env`文件，其次执行如下指令，完成Python环境配置、前后端配置

```
cd agent-service
uv venv --python 3.12
source .venv/bin/activate
uv sync

cd backend
go mod tidy

cd frontend
npm install
```

项目启动：四个终端

```
cd agent-service
./start_mcp_server.sh
# 运行在 http://localhost:8006/mcp_demo

cd agent-service
source .venv/bin/activate
python -m uvicorn src.api.main:app --reload --port 8000

cd backend
go run cmd/main.go

cd frontend
npm run dev -- --host
```

