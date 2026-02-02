# MCP Server 集成文档

## 概述

您的 MCP Server (`shttp_demo_server.py`) 已成功集成到 Agent 服务中。Agent 现在可以自动调用 MCP Server 提供的工具。

## 📁 相关文件

- **MCP Server**: [src/tools/shttp_demo_server.py](src/tools/shttp_demo_server.py)
- **MCP 客户端**: [src/tools/mcp_http_client.py](src/tools/mcp_http_client.py)
- **增强 Agent**: [src/agent/mcp_agent.py](src/agent/mcp_agent.py)

## 🚀 启动服务

### 方式 1: 手动启动（推荐用于开发调试）

#### 终端 1 - MCP Server
```bash
cd agent-service
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 启动 MCP Server
python -m src.tools.shttp_demo_server
```

**输出示例**:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8006 (Press CTRL+C to quit)
```

#### 终端 2 - Agent 服务
```bash
cd agent-service
source .venv/bin/activate

# 确保 .env 中配置了 MCP_SERVER_URL
# MCP_SERVER_URL=http://localhost:8006/mcp_demo

# 启动 Agent 服务
python -m uvicorn src.api.main:app --reload --port 8000
```

### 方式 2: 使用启动脚本

**Linux/macOS**:
```bash
# 给脚本添加执行权限
chmod +x start_mcp_server.sh

# 启动 MCP Server
./start_mcp_server.sh
```

**Windows**:
```cmd
start_mcp_server.bat
```

## 🔧 配置说明

### 环境变量 (.env)

```bash
# MCP Server 配置
MCP_SERVER_URL=http://localhost:8006/mcp_demo
```

如果 MCP Server 运行在不同的端口或主机，请修改此配置。

## 🛠 MCP Server 提供的工具

根据您的 `shttp_demo_server.py`，当前提供以下工具：

1. **add(a: int, b: int) -> int**
   - 功能：两数相加
   - 示例调用：`add(5, 3)` → 返回 `8`

2. **get_weather(location: str) -> str**
   - 功能：获取天气信息
   - 示例调用：`get_weather("New York")` → 返回 `"It's always sunny in New York"`

## 💬 使用示例

### 1. 通过聊天界面调用

启动完整系统后，在前端输入：

**示例 1 - 调用 add 工具**:
```
用户: 帮我计算 25 + 17
Agent: [自动调用 add(25, 17)] → 返回 42
Agent: 25 加 17 等于 42。
```

**示例 2 - 调用 get_weather 工具**:
```
用户: New York 的天气怎么样？
Agent: [自动调用 get_weather("New York")]
Agent: It's always sunny in New York
```

### 2. 通过 API 测试

**REST API 测试**:
```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "帮我计算 10 + 20",
    "session_id": "test123"
  }'
```

**SSE 流式测试**:
```bash
curl -X POST http://localhost:8000/agent/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "计算 5 + 3",
    "session_id": "test123"
  }'
```

## 🔍 工作原理

### 完整调用流程

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   用户输入   │ --> │ MCPEnhanced  │ --> │ MCP HTTP    │ --> │ MCP Server   │
│   消息      │     │    Agent     │     │  Client     │     │ (FastMCP)    │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
                           │                     │                    │
                           │   1. 分析意图        │                    │
                           │   需要调用工具?      │                    │
                           │                     │                    │
                           │   2. 获取工具列表    │ ---- GET ------>  │
                           │                     │ <--- tools -----  │
                           │                     │                    │
                           │   3. 调用工具        │ ---- POST -----> │
                           │                     │  tool_name: add   │
                           │                     │  args: {a:5,b:3}  │
                           │                     │ <--- result: 8 -- │
                           │                     │                    │
                           │   4. 生成响应        │                    │
                           │   (基于工具结果)     │                    │
                           v                     v                    v
                     返回给用户
```

### 关键代码逻辑

1. **Agent 启动时** ([src/api/main.py:46-64](src/api/main.py))
   - 创建 `MCPEnhancedAgent` 实例
   - 传入 `mcp_server_url` 参数

2. **用户发送消息时** ([src/agent/mcp_agent.py:97-133](src/agent/mcp_agent.py))
   - `_analyze_intent()`: LLM 分析是否需要调用工具
   - 如需调用，提取工具名称和参数

3. **调用 MCP 工具** ([src/agent/mcp_agent.py:139-166](src/agent/mcp_agent.py))
   - `_call_tool()`: 通过 MCP 客户端调用远程工具
   - 使用 JSONRPC 2.0 协议通信

4. **生成最终响应** ([src/agent/mcp_agent.py:168-193](src/agent/mcp_agent.py))
   - `_respond()`: LLM 基于工具结果生成自然语言回复

## 🔌 添加自定义 MCP 工具

### 在您的 MCP Server 中添加新工具

编辑 `src/tools/shttp_demo_server.py`:

```python
from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")

# 现有工具
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# 新增工具 - 示例 1: 字符串处理
@mcp.tool()
def reverse_string(text: str) -> str:
    """Reverse a string"""
    return text[::-1]

# 新增工具 - 示例 2: 数据查询
@mcp.tool()
def get_user_info(user_id: int) -> dict:
    """Get user information by ID"""
    # 模拟数据库查询
    return {
        "id": user_id,
        "name": f"User_{user_id}",
        "email": f"user{user_id}@example.com"
    }

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8006, path="/mcp_demo")
```

### 重启 MCP Server

```bash
# 停止现有服务器 (Ctrl+C)
# 重新启动
python -m src.tools.shttp_demo_server
```

**Agent 会自动发现新工具，无需修改 Agent 代码！**

## 🐛 故障排查

### 问题 1: Agent 无法连接到 MCP Server

**现象**:
```
Failed to load MCP tools: Connection refused
```

**解决**:
1. 确保 MCP Server 正在运行
2. 检查端口是否正确（默认 8006）
3. 验证 `.env` 中的 `MCP_SERVER_URL` 配置

```bash
# 测试 MCP Server 是否可访问
curl http://localhost:8006/mcp_demo
```

### 问题 2: 工具调用失败

**现象**:
```
MCP tool call error: Tool 'xxx' not found
```

**解决**:
1. 检查工具名称是否正确
2. 确保 MCP Server 已注册该工具
3. 查看 MCP Server 日志

### 问题 3: Agent 未调用 MCP 工具

**现象**: Agent 直接回复，不调用工具

**原因**: LLM 可能没有识别到需要使用工具

**解决**:
1. 使用更明确的指令，如 "使用 add 工具计算..."
2. 确保工具描述清晰（`@mcp.tool()` 的 docstring）
3. 检查 Agent 日志，查看意图分析结果

## 📊 监控和日志

### 查看 MCP Server 日志

MCP Server 会输出请求日志：
```
INFO:     127.0.0.1:xxxxx - "POST /mcp_demo HTTP/1.1" 200 OK
```

### 查看 Agent 日志

Agent 服务日志会显示工具调用：
```
INFO - Calling MCP tool: add with args: {'a': 5, 'b': 3}
```

### 调试模式

设置更详细的日志级别：

**.env**:
```bash
LOG_LEVEL=DEBUG
```

## 🚀 高级用法

### 1. 连接多个 MCP Server

修改 Agent 以支持多个 MCP Server：

```python
# 在 mcp_agent.py 中
mcp_clients = [
    MCPHttpClient("http://localhost:8006/mcp_demo"),
    MCPHttpClient("http://localhost:8007/another_mcp"),
]
```

### 2. 工具权限控制

在调用工具前添加验证：

```python
def _call_tool(self, state: AgentState) -> AgentState:
    tool_name = state.get("tool_call", {}).get("name")

    # 权限检查
    if tool_name in RESTRICTED_TOOLS:
        if not self.has_permission(tool_name):
            state["tool_result"] = "无权限调用此工具"
            return state

    # ... 执行工具调用
```

### 3. 工具调用缓存

对相同参数的工具调用进行缓存：

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_tool_call(tool_name: str, args_hash: str):
    # 缓存工具调用结果
    pass
```

## 📝 测试清单

- [ ] MCP Server 成功启动在 8006 端口
- [ ] Agent 服务成功连接到 MCP Server
- [ ] 通过聊天界面调用 `add` 工具成功
- [ ] 通过聊天界面调用 `get_weather` 工具成功
- [ ] 添加自定义工具并测试成功
- [ ] 查看完整的端到端日志

## 🎯 下一步

1. **扩展 MCP 工具集**：根据业务需求添加更多工具
2. **优化意图识别**：调整 prompt 提高工具调用准确率
3. **添加工具文档**：为每个工具编写详细的使用说明
4. **实现工具组合**：支持一次对话调用多个工具
5. **集成真实 MCP Server**：替换 demo server 为生产级 MCP 服务

## 📚 参考资料

- [FastMCP 文档](https://github.com/jlowin/fastmcp)
- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [MCP 协议规范](https://modelcontextprotocol.io/)
