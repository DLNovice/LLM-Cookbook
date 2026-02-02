# Agent 聊天系统部署指南

## 系统要求

- Python 3.11+
- Golang 1.21+
- Node.js 18+
- uv (Python 包管理器)

## 安装步骤

### 1. 安装 Python 环境 (Agent 服务)

```bash
cd agent-service

# 使用 uv 创建虚拟环境
uv venv

# 激活虚拟环境
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# 安装依赖
uv pip install -e .

# 复制环境变量配置
cp .env.example .env

# 编辑 .env 文件，设置 OpenRouter API Key
# OPENROUTER_API_KEY=your_api_key_here
```

### 2. 配置 Golang 后端

```bash
cd ../backend

# 下载依赖
go mod download

# 复制环境变量配置
cp .env.example .env

# 编辑 .env 文件（可选，使用默认配置即可）
```

### 3. 配置 Vue 前端

```bash
cd ../frontend

# 安装依赖
npm install

# 环境变量已配置（.env 文件）
```

## 运行服务

### 方式 1: 分别运行（推荐用于开发）

**终端 1 - Agent 服务:**
```bash
cd agent-service
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m uvicorn src.api.main:app --reload --port 8000
```

**终端 2 - Golang 后端:**
```bash
cd backend
go run cmd/main.go
```

**终端 3 - Vue 前端:**
```bash
cd frontend
npm run dev
```

### 方式 2: 使用启动脚本（待创建）

可以创建一个 `start.sh` 脚本来同时启动所有服务。

## 访问应用

启动所有服务后：

- **前端界面**: http://localhost:5173
- **Golang 后端**: http://localhost:8080
- **Agent 服务**: http://localhost:8000

## 服务健康检查

### 检查 Agent 服务
```bash
curl http://localhost:8000/health
```

### 检查 Golang 后端
```bash
curl http://localhost:8080/api/health
```

## 常见问题排查

### 1. Agent 服务启动失败

**问题**: `OPENROUTER_API_KEY not set`

**解决**: 在 `agent-service/.env` 中设置正确的 API Key

### 2. WebSocket 连接失败

**问题**: 前端无法连接 WebSocket

**解决**:
- 确保 Golang 后端运行在 8080 端口
- 检查防火墙设置
- 检查浏览器控制台错误信息

### 3. 端口冲突

**问题**: 端口已被占用

**解决**:
- Agent 服务: 修改 `.env` 中的 `PORT`
- Golang 后端: 修改 `.env` 中的 `SERVER_PORT`
- Vue 前端: 修改 `vite.config.js` 中的 `port`

### 4. CORS 错误

**问题**: 跨域请求失败

**解决**:
- 后端已配置 CORS，允许所有来源
- 如需限制，修改 `backend/cmd/main.go` 中的 CORS 配置

## 生产环境部署

### Agent 服务

```bash
cd agent-service
source .venv/bin/activate

# 使用 gunicorn 或 uvicorn 运行
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Golang 后端

```bash
cd backend

# 编译
go build -o bin/server cmd/main.go

# 运行
./bin/server
```

### Vue 前端

```bash
cd frontend

# 构建
npm run build

# 使用 nginx 或其他 Web 服务器托管 dist/ 目录
```

## 性能优化建议

1. **Agent 服务**:
   - 使用多个 worker 进程
   - 配置合适的超时时间
   - 启用请求缓存

2. **Golang 后端**:
   - 启用连接池
   - 配置合适的 WebSocket 缓冲区大小
   - 使用负载均衡

3. **Vue 前端**:
   - 启用生产环境构建优化
   - 使用 CDN 加速静态资源
   - 启用 gzip 压缩

## 监控和日志

### 日志位置

- Agent 服务: 控制台输出，可配置到文件
- Golang 后端: 控制台输出
- Vue 前端: 浏览器控制台

### 推荐监控工具

- Prometheus + Grafana (性能监控)
- ELK Stack (日志分析)
- Sentry (错误追踪)

## 扩展功能

### 集成自定义 MCP 工具

在 `agent-service/src/tools/` 中添加新的工具模块：

```python
# my_tool.py
def my_custom_tool(param: str) -> dict:
    # 工具实现
    return {"result": "success"}

# 在 agent_service.py 中注册
from tools.mcp_manager import mcp_manager
from tools.my_tool import my_custom_tool

mcp_manager.register_tool(
    "my_tool",
    my_custom_tool,
    "自定义工具描述"
)
```

### 添加用户认证

1. 在 Golang 后端添加 JWT 中间件
2. 在 WebSocket 连接时验证 token
3. 在前端登录后存储 token

### 数据持久化

1. 添加数据库连接（PostgreSQL/MongoDB）
2. 存储会话历史
3. 实现消息检索功能

## 许可证

MIT License
