"""
Agent 配置管理模块
==================
集中管理 MCP Server、记忆系统、LLM 等配置
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(override=False)


@dataclass
class LLMConfig:
    """LLM 配置"""
    model: str = field(default_factory=lambda: os.getenv("MODEL_NAME", "gpt-4"))
    api_key: str = field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""))
    base_url: str = field(default_factory=lambda: os.getenv("BASE_URL", ""))
    temperature: float = 0.3


@dataclass
class MCPServerConfig:
    """单个 MCP Server 配置"""
    name: str
    transport: str = "http"
    url: str = ""


@dataclass
class MCPConfig:
    """MCP 配置"""
    servers: Dict[str, MCPServerConfig] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "MCPConfig":
        """从环境变量加载 MCP 配置"""
        # 默认配置，可通过环境变量覆盖
        default_url = os.getenv("MCP_SERVER_URL", "http://0.0.0.0:4202/psa_temp")
        
        servers = {
            "psa_tools": MCPServerConfig(
                name="psa_tools",
                transport="http",
                url=default_url
            )
        }
        return cls(servers=servers)

    def to_client_config(self) -> Dict[str, Dict[str, Any]]:
        """转换为 MultiServerMCPClient 所需的配置格式"""
        return {
            name: {
                "transport": cfg.transport,
                "url": cfg.url
            }
            for name, cfg in self.servers.items()
        }


@dataclass
class MilvusConfig:
    """Milvus 向量数据库配置"""
    host: str = field(default_factory=lambda: os.getenv("MILVUS_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("MILVUS_PORT", "19530")))
    collection_name: str = "agent_memory"


@dataclass
class MemoryConfig:
    """记忆系统配置"""
    enabled: bool = True
    milvus: MilvusConfig = field(default_factory=MilvusConfig)
    
    # 对话压缩配置
    max_messages_before_compress: int = 10  # 超过此数量触发压缩
    keep_recent_messages: int = 5  # 压缩时保留最近的消息数

    def to_mem0_config(self, llm_config: LLMConfig) -> Dict[str, Any]:
        """转换为 Mem0 配置格式"""
        return {
            "vector_store": {
                "provider": "milvus",
                "config": {
                    "collection_name": self.milvus.collection_name,
                    "host": self.milvus.host,
                    "port": self.milvus.port,
                }
            },
            "llm": {
                "provider": "openai",
                "config": {
                    "model": llm_config.model,
                    "api_key": llm_config.api_key,
                    "openai_base_url": llm_config.base_url,
                }
            }
        }


@dataclass
class PlanExecuteConfig:
    """Plan-and-Execute Agent 完整配置"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    mcp: MCPConfig = field(default_factory=MCPConfig.from_env)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    
    # 执行控制
    max_replan_count: int = 3  # 最大重规划次数
    recursion_limit: int = 100  # LangGraph 递归限制

    @classmethod
    def from_env(cls) -> "PlanExecuteConfig":
        """从环境变量创建配置"""
        return cls(
            llm=LLMConfig(),
            mcp=MCPConfig.from_env(),
            memory=MemoryConfig()
        )


# 全局默认配置实例
default_config = PlanExecuteConfig.from_env()
