"""
LangGraph Weather Agent Implementation
基于 LangGraph 的天气查询助手
"""
from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
import operator
import logging
import re

from ..tools.weather import get_weather, format_weather_response
from ..tools.mcp_manager import mcp_manager

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """Agent 状态定义"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_step: str
    weather_data: dict | None


class WeatherAgent:
    """天气查询 Agent"""

    def __init__(self, model_name: str = "openai/gpt-4o-mini", api_key: str = None, base_url: str = None):
        """
        初始化 Weather Agent

        Args:
            model_name: 模型名称
            api_key: API 密钥
            base_url: API base URL (用于 OpenRouter)
        """
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=0.7,
            streaming=True
        )

        # 构建 LangGraph 工作流
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """构建 LangGraph 工作流"""
        workflow = StateGraph(AgentState)

        # 添加节点
        workflow.add_node("analyze_intent", self._analyze_intent)
        workflow.add_node("query_weather", self._query_weather)
        workflow.add_node("respond", self._respond)

        # 设置入口点
        workflow.set_entry_point("analyze_intent")

        # 添加条件边
        workflow.add_conditional_edges(
            "analyze_intent",
            self._route_after_intent,
            {
                "weather": "query_weather",
                "chat": "respond"
            }
        )

        workflow.add_edge("query_weather", "respond")
        workflow.add_edge("respond", END)

        return workflow.compile()

    def _analyze_intent(self, state: AgentState) -> AgentState:
        """分析用户意图"""
        messages = state["messages"]
        last_message = messages[-1].content if messages else ""

        logger.info(f"Analyzing intent for: {last_message}")

        # 简单的意图识别
        weather_keywords = ["天气", "温度", "气温", "weather", "temperature"]
        is_weather_query = any(keyword in last_message.lower() for keyword in weather_keywords)

        state["current_step"] = "weather" if is_weather_query else "chat"
        return state

    def _route_after_intent(self, state: AgentState) -> Literal["weather", "chat"]:
        """根据意图路由"""
        return state["current_step"]

    def _query_weather(self, state: AgentState) -> AgentState:
        """查询天气"""
        messages = state["messages"]
        last_message = messages[-1].content if messages else ""

        # 提取城市名称
        city = self._extract_city(last_message)

        if not city:
            city = "北京"  # 默认城市

        logger.info(f"Querying weather for city: {city}")

        # 调用天气工具
        weather_data = get_weather(city)
        state["weather_data"] = weather_data

        return state

    def _extract_city(self, text: str) -> str | None:
        """从文本中提取城市名称"""
        # 简单的正则匹配
        patterns = [
            r"(?:的)?([北上广深杭成都重庆天津南京武汉西安]{2,})(?:的)?(?:天气|气温)?",
            r"(?:weather|temperature)\s+(?:in|of|for)\s+(\w+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        return None

    def _respond(self, state: AgentState) -> AgentState:
        """生成响应"""
        messages = state["messages"]
        weather_data = state.get("weather_data")

        # 构建系统提示
        system_prompt = """你是一个友好的天气查询助手。
当用户询问天气时,你应该基于提供的天气数据给出友好的回复。
当用户进行普通聊天时,你应该自然地回应。
保持简洁、友好的语气。"""

        # 如果有天气数据,添加到上下文
        context_messages = [SystemMessage(content=system_prompt)]

        if weather_data:
            weather_info = format_weather_response(weather_data)
            context_messages.append(
                SystemMessage(content=f"当前查询到的天气信息:\n{weather_info}")
            )

        context_messages.extend(messages)

        # 调用 LLM 生成响应
        response = self.llm.invoke(context_messages)

        # 添加到消息历史
        state["messages"] = state["messages"] + [response]

        return state

    async def stream_chat(self, message: str, session_id: str = "default"):
        """
        流式聊天接口

        Args:
            message: 用户消息
            session_id: 会话 ID

        Yields:
            流式响应块
        """
        # 初始化状态
        initial_state: AgentState = {
            "messages": [HumanMessage(content=message)],
            "current_step": "",
            "weather_data": None
        }

        # 执行工作流
        try:
            # 运行直到 respond 节点
            state = initial_state
            state = self._analyze_intent(state)

            if state["current_step"] == "weather":
                state = self._query_weather(state)

            # 流式生成响应
            messages = state["messages"]
            weather_data = state.get("weather_data")

            system_prompt = """你是一个友好的天气查询助手。
当用户询问天气时,你应该基于提供的天气数据给出友好的回复。
当用户进行普通聊天时,你应该自然地回应。
保持简洁、友好的语气。"""

            context_messages = [SystemMessage(content=system_prompt)]

            if weather_data:
                weather_info = format_weather_response(weather_data)
                context_messages.append(
                    SystemMessage(content=f"当前查询到的天气信息:\n{weather_info}")
                )

            context_messages.extend(messages)

            # 流式调用
            async for chunk in self.llm.astream(context_messages):
                if chunk.content:
                    yield chunk.content

        except Exception as e:
            logger.error(f"Error in stream_chat: {e}")
            yield f"抱歉,处理您的请求时出现错误: {str(e)}"

    def chat(self, message: str, session_id: str = "default") -> str:
        """
        同步聊天接口

        Args:
            message: 用户消息
            session_id: 会话 ID

        Returns:
            Agent 响应
        """
        initial_state: AgentState = {
            "messages": [HumanMessage(content=message)],
            "current_step": "",
            "weather_data": None
        }

        # 执行完整工作流
        final_state = self.graph.invoke(initial_state)

        # 返回最后一条 AI 消息
        ai_messages = [msg for msg in final_state["messages"] if isinstance(msg, AIMessage)]
        return ai_messages[-1].content if ai_messages else "抱歉,我无法处理您的请求。"
