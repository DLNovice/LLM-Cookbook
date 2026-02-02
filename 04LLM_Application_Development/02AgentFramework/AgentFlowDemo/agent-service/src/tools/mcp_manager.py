"""
MCP 工具管理器
支持动态加载和管理 MCP 工具
"""
from typing import List, Dict, Any, Callable
import importlib.util
import logging

logger = logging.getLogger(__name__)


class MCPToolManager:
    """MCP 工具管理器"""

    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_descriptions: Dict[str, str] = {}

    def register_tool(
        self,
        name: str,
        tool_func: Callable,
        description: str = ""
    ):
        """
        注册 MCP 工具

        Args:
            name: 工具名称
            tool_func: 工具函数
            description: 工具描述
        """
        self.tools[name] = tool_func
        self.tool_descriptions[name] = description
        logger.info(f"Registered MCP tool: {name}")

    def get_tool(self, name: str) -> Callable:
        """获取工具函数"""
        return self.tools.get(name)

    def list_tools(self) -> List[Dict[str, str]]:
        """列出所有可用工具"""
        return [
            {
                "name": name,
                "description": self.tool_descriptions.get(name, "")
            }
            for name in self.tools.keys()
        ]

    def execute_tool(self, name: str, **kwargs) -> Any:
        """
        执行工具

        Args:
            name: 工具名称
            **kwargs: 工具参数

        Returns:
            工具执行结果
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")

        try:
            return tool(**kwargs)
        except Exception as e:
            logger.error(f"Error executing tool '{name}': {e}")
            raise


# 全局工具管理器实例
mcp_manager = MCPToolManager()
