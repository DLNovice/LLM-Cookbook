"""
FastAPI 主应用
提供 HTTP 和 SSE 接口供 Golang 后端调用
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
import logging
from typing import AsyncGenerator

from ..agent.weather_agent import WeatherAgent
from ..agent.mcp_agent import MCPEnhancedAgent
from ..utils.config import get_settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化配置
settings = get_settings()

# 创建 FastAPI 应用
app = FastAPI(
    title="Weather Agent Service",
    description="LangGraph-based Weather Query Agent",
    version="0.1.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 Agent
agent: MCPEnhancedAgent | None = None


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化 Agent"""
    global agent

    logger.info("Initializing MCP Enhanced Agent...")

    if not settings.OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not set. Agent may not work properly.")

    # 使用 MCP Enhanced Agent
    agent = MCPEnhancedAgent(
        model_name=settings.DEFAULT_MODEL,
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
        mcp_server_url=settings.MCP_SERVER_URL  # 新增 MCP Server URL
    )

    logger.info("MCP Enhanced Agent initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    logger.info("Shutting down Agent Service...")
    if agent:
        await agent.cleanup()


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str
    session_id: str


@app.get("/")
async def root():
    """健康检查"""
    return {
        "service": "Weather Agent Service",
        "status": "running",
        "version": "0.1.0"
    }


@app.post("/agent/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    同步聊天接口

    Args:
        request: 聊天请求

    Returns:
        聊天响应
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        response = await agent.chat(
            message=request.message,
            session_id=request.session_id
        )

        return ChatResponse(
            response=response,
            session_id=request.session_id
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/stream")
async def stream_chat(request: ChatRequest):
    """
    流式聊天接口 (SSE)

    Args:
        request: 聊天请求

    Returns:
        SSE 事件流
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    async def event_generator() -> AsyncGenerator[dict, None]:
        """SSE 事件生成器"""
        try:
            async for chunk in agent.stream_chat(
                message=request.message,
                session_id=request.session_id
            ):
                # 发送数据块
                yield {
                    "event": "message",
                    "data": chunk
                }

            # 发送结束标记
            yield {
                "event": "done",
                "data": "[DONE]"
            }

        except Exception as e:
            logger.error(f"Error in stream_chat: {e}")
            yield {
                "event": "error",
                "data": str(e)
            }

    return EventSourceResponse(event_generator())


@app.get("/health")
async def health_check():
    """详细健康检查"""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "settings": {
            "model": settings.DEFAULT_MODEL,
            "base_url": settings.OPENROUTER_BASE_URL,
            "api_key_configured": bool(settings.OPENROUTER_API_KEY)
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
