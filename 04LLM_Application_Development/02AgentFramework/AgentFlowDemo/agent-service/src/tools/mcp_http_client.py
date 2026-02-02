"""
MCP HTTP 客户端
用于连接和调用基于 HTTP 的 MCP Server
"""
import httpx
import logging
from typing import Any, Dict, List, Optional
import json

logger = logging.getLogger(__name__)


class MCPHttpClient:
    """MCP HTTP 客户端（支持 streamable-http）"""

    def __init__(self, base_url: str):
        """
        初始化 MCP HTTP 客户端

        Args:
            base_url: MCP Server 的基础 URL，例如 "http://localhost:8006/mcp_demo"
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)
        self.tools_cache: Optional[List[Dict]] = None

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        获取 MCP Server 提供的所有工具列表

        Returns:
            工具列表，每个工具包含 name, description, parameters 等信息
        """
        if self.tools_cache:
            return self.tools_cache

        try:
            # FastMCP 的 streamable-http 协议通常使用 POST /tools 或类似端点
            # 这里使用标准的 MCP 协议格式
            response = await self.client.post(
                self.base_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {}
                }
            )
            response.raise_for_status()

            result = response.json()
            tools = result.get("result", {}).get("tools", [])

            self.tools_cache = tools
            logger.info(f"Loaded {len(tools)} tools from MCP server: {[t['name'] for t in tools]}")

            return tools

        except Exception as e:
            logger.error(f"Failed to list MCP tools: {e}")
            return []

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        调用 MCP Server 上的工具

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果
        """
        try:
            logger.info(f"Calling MCP tool: {tool_name} with args: {arguments}")

            response = await self.client.post(
                self.base_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                }
            )
            response.raise_for_status()

            result = response.json()

            # 检查是否有错误
            if "error" in result:
                error_msg = result["error"].get("message", "Unknown error")
                logger.error(f"MCP tool call error: {error_msg}")
                return {"error": error_msg}

            # 返回结果
            tool_result = result.get("result", {})
            content = tool_result.get("content", [])

            # 提取文本内容
            if content and isinstance(content, list) and len(content) > 0:
                return content[0].get("text", str(tool_result))

            return str(tool_result)

        except Exception as e:
            logger.error(f"Failed to call MCP tool '{tool_name}': {e}")
            return {"error": str(e)}

    async def get_tool_schema(self, tool_name: str) -> Optional[Dict]:
        """
        获取指定工具的 schema

        Args:
            tool_name: 工具名称

        Returns:
            工具 schema
        """
        tools = await self.list_tools()
        for tool in tools:
            if tool.get("name") == tool_name:
                return tool
        return None


class MCPToolAdapter:
    """
    MCP 工具适配器
    将 MCP 工具转换为 LangChain 可调用的工具
    """

    def __init__(self, mcp_client: MCPHttpClient):
        """
        初始化适配器

        Args:
            mcp_client: MCP HTTP 客户端
        """
        self.mcp_client = mcp_client
        self.tools_map: Dict[str, Dict] = {}

    async def load_tools(self) -> List[Dict]:
        """
        加载所有 MCP 工具

        Returns:
            工具描述列表
        """
        mcp_tools = await self.mcp_client.list_tools()

        for tool in mcp_tools:
            tool_name = tool.get("name")
            self.tools_map[tool_name] = tool

        return list(self.tools_map.values())

    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """
        执行 MCP 工具

        Args:
            tool_name: 工具名称
            **kwargs: 工具参数

        Returns:
            工具执行结果
        """
        if tool_name not in self.tools_map:
            return f"Error: Tool '{tool_name}' not found"

        result = await self.mcp_client.call_tool(tool_name, kwargs)
        return result

    def get_tools_description(self) -> str:
        """
        获取所有工具的描述信息

        Returns:
            工具描述文本
        """
        if not self.tools_map:
            return "No MCP tools available"

        descriptions = []
        for tool_name, tool_info in self.tools_map.items():
            desc = tool_info.get("description", "No description")
            params = tool_info.get("inputSchema", {}).get("properties", {})
            param_desc = ", ".join([f"{k}: {v.get('type', 'any')}" for k, v in params.items()])

            descriptions.append(f"- {tool_name}({param_desc}): {desc}")

        return "\n".join(descriptions)
