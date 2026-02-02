"""
Enhanced LangGraph Agent with MCP Support
支持 MCP 工具集成的增强型 Agent
"""
from typing import TypedDict, Annotated, Sequence, Literal, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
import operator
import logging
import re
import json

from ..tools.weather import get_weather, format_weather_response
from ..tools.mcp_http_client import MCPHttpClient, MCPToolAdapter

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """Agent 状态定义"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_step: str
    tool_call: dict | None
    tool_result: str | None


class MCPEnhancedAgent:
    """支持 MCP 的增强型 Agent"""

    def __init__(
        self,
        model_name: str = "openai/gpt-4o-mini",
        api_key: str = None,
        base_url: str = None,
        mcp_server_url: str = None
    ):
        """
        初始化 MCP Enhanced Agent

        Args:
            model_name: 模型名称
            api_key: API 密钥
            base_url: API base URL (用于 OpenRouter)
            mcp_server_url: MCP Server URL (例如 http://localhost:8006/mcp_demo)
        """
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=0.7,
            streaming=True
        )

        # 初始化 MCP 客户端
        self.mcp_client: Optional[MCPHttpClient] = None
        self.mcp_adapter: Optional[MCPToolAdapter] = None
        self.mcp_server_url = mcp_server_url
        self.mcp_tools_loaded = False

        # 构建 LangGraph 工作流
        self.graph = self._build_graph()

    async def _ensure_mcp_tools_loaded(self):
        """确保 MCP 工具已加载"""
        if self.mcp_tools_loaded or not self.mcp_server_url:
            return

        try:
            logger.info(f"Connecting to MCP server: {self.mcp_server_url}")
            self.mcp_client = MCPHttpClient(self.mcp_server_url)
            self.mcp_adapter = MCPToolAdapter(self.mcp_client)

            tools = await self.mcp_adapter.load_tools()
            logger.info(f"Loaded {len(tools)} MCP tools")

            self.mcp_tools_loaded = True
        except Exception as e:
            logger.error(f"Failed to load MCP tools: {e}")
            self.mcp_tools_loaded = False

    def _build_graph(self) -> StateGraph:
        """构建 LangGraph 工作流"""
        workflow = StateGraph(AgentState)

        # 添加节点
        workflow.add_node("analyze_intent", self._analyze_intent)
        workflow.add_node("call_tool", self._call_tool)
        workflow.add_node("respond", self._respond)

        # 设置入口点
        workflow.set_entry_point("analyze_intent")

        # 添加条件边
        workflow.add_conditional_edges(
            "analyze_intent",
            self._route_after_intent,
            {
                "use_tool": "call_tool",
                "direct_chat": "respond"
            }
        )

        workflow.add_edge("call_tool", "respond")
        workflow.add_edge("respond", END)

        return workflow.compile()

    async def _analyze_intent(self, state: AgentState) -> AgentState:
        """分析用户意图并决定是否需要调用工具"""
        messages = state["messages"]
        last_message = messages[-1].content if messages else ""

        logger.info(f"Analyzing intent for: {last_message}")

        # 确保 MCP 工具已加载
        await self._ensure_mcp_tools_loaded()

        # 构建工具描述
        tools_description = self._get_available_tools_description()

        # 使用 LLM 分析是否需要调用工具
        analysis_prompt = f"""你是一个智能助手。用户说："{last_message}"

你有以下工具可用：
{tools_description}

请分析用户的意图，并决定：
1. 如果需要调用工具，请输出 JSON 格式：{{"action": "use_tool", "tool_name": "工具名", "arguments": {{"参数": "值"}}}}
2. 如果不需要工具，直接聊天，请输出：{{"action": "direct_chat"}}

只输出 JSON，不要其他内容。"""

        try:
            analysis_result = self.llm.invoke([HumanMessage(content=analysis_prompt)])
            analysis_text = analysis_result.content.strip()

            # 提取 JSON
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                analysis_json = json.loads(json_match.group())

                if analysis_json.get("action") == "use_tool":
                    state["current_step"] = "use_tool"
                    state["tool_call"] = {
                        "name": analysis_json.get("tool_name"),
                        "arguments": analysis_json.get("arguments", {})
                    }
                else:
                    state["current_step"] = "direct_chat"
            else:
                state["current_step"] = "direct_chat"

        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            state["current_step"] = "direct_chat"

        return state

    def _route_after_intent(self, state: AgentState) -> Literal["use_tool", "direct_chat"]:
        """根据意图路由"""
        return state["current_step"]

    async def _call_tool(self, state: AgentState) -> AgentState:
        """调用工具"""
        tool_call = state.get("tool_call")
        if not tool_call:
            state["tool_result"] = "错误：没有工具调用信息"
            return state

        tool_name = tool_call.get("name")
        arguments = tool_call.get("arguments", {})

        logger.info(f"Calling tool: {tool_name} with {arguments}")

        # 内置工具
        if tool_name == "get_weather":
            city = arguments.get("location") or arguments.get("city", "北京")
            weather_data = get_weather(city)
            result = format_weather_response(weather_data)
            state["tool_result"] = result
            return state

        # MCP 工具
        if self.mcp_adapter:
            try:
                result = await self.mcp_adapter.execute_tool(tool_name, **arguments)
                state["tool_result"] = str(result)
            except Exception as e:
                logger.error(f"MCP tool call failed: {e}")
                state["tool_result"] = f"工具调用失败: {str(e)}"
        else:
            state["tool_result"] = f"工具 '{tool_name}' 不可用"

        return state

    async def _respond(self, state: AgentState) -> AgentState:
        """生成响应"""
        messages = state["messages"]
        tool_result = state.get("tool_result")

        # 构建系统提示
        system_prompt = """你是一个友好、智能的助手。
你可以使用工具来帮助用户完成任务，也可以进行普通对话。
保持简洁、友好的语气。"""

        context_messages = [SystemMessage(content=system_prompt)]

        # 如果有工具结果，添加到上下文
        if tool_result:
            context_messages.append(
                SystemMessage(content=f"工具执行结果:\n{tool_result}\n\n请基于这个结果回复用户。")
            )

        context_messages.extend(messages)

        # 调用 LLM 生成响应
        response = self.llm.invoke(context_messages)
        state["messages"] = state["messages"] + [response]

        return state

    def _get_available_tools_description(self) -> str:
        """获取所有可用工具的描述"""
        descriptions = []

        # 内置工具
        descriptions.append("- get_weather(location: str): 查询指定地点的天气信息")

        # MCP 工具
        if self.mcp_adapter and self.mcp_adapter.tools_map:
            for tool_name, tool_info in self.mcp_adapter.tools_map.items():
                desc = tool_info.get("description", "No description")
                params = tool_info.get("inputSchema", {}).get("properties", {})
                param_list = []
                for param_name, param_info in params.items():
                    param_type = param_info.get("type", "any")
                    param_list.append(f"{param_name}: {param_type}")

                param_str = ", ".join(param_list) if param_list else ""
                descriptions.append(f"- {tool_name}({param_str}): {desc}")

        return "\n".join(descriptions) if descriptions else "无可用工具"

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
            "tool_call": None,
            "tool_result": None
        }

        try:
            # 分析意图
            state = await self._analyze_intent(initial_state)

            # 如果需要调用工具
            if state["current_step"] == "use_tool":
                state = await self._call_tool(state)

            # 流式生成响应
            messages = state["messages"]
            tool_result = state.get("tool_result")

            system_prompt = """你是一个友好、智能的助手。
你可以使用工具来帮助用户完成任务，也可以进行普通对话。
保持简洁、友好的语气。"""

            context_messages = [SystemMessage(content=system_prompt)]

            if tool_result:
                context_messages.append(
                    SystemMessage(content=f"工具执行结果:\n{tool_result}\n\n请基于这个结果回复用户。")
                )

            context_messages.extend(messages)

            # 流式调用
            async for chunk in self.llm.astream(context_messages):
                if chunk.content:
                    yield chunk.content

        except Exception as e:
            logger.error(f"Error in stream_chat: {e}")
            yield f"抱歉，处理您的请求时出现错误: {str(e)}"

    async def chat(self, message: str, session_id: str = "default") -> str:
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
            "tool_call": None,
            "tool_result": None
        }

        # 分析意图
        state = await self._analyze_intent(initial_state)

        # 如果需要调用工具
        if state["current_step"] == "use_tool":
            state = await self._call_tool(state)

        # 生成响应
        state = await self._respond(state)

        # 返回最后一条 AI 消息
        ai_messages = [msg for msg in state["messages"] if isinstance(msg, AIMessage)]
        return ai_messages[-1].content if ai_messages else "抱歉，我无法处理您的请求。"

    async def cleanup(self):
        """清理资源"""
        if self.mcp_client:
            await self.mcp_client.close()
