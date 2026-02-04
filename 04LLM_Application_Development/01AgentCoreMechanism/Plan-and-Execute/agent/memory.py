"""
Agent 记忆系统模块
==================
基于 Mem0 实现的记忆管理，支持：
1. 语义记忆存储与检索
2. 对话历史压缩与总结
3. 执行经验记忆
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from app.agent.config import PlanExecuteConfig, default_config

logger = logging.getLogger(__name__)


# =========================================================
# 1. 对话压缩器
# =========================================================

COMPRESS_PROMPT = """你是一个对话总结专家。请将以下对话历史压缩为一个简洁的摘要，保留关键信息。

## 对话历史
{conversation}

## 要求
1. 保留用户的核心目标和意图
2. 保留重要的决策和结论
3. 保留关键的执行结果
4. 去除冗余的中间过程
5. 输出不超过 500 字

## 摘要
"""


class ConversationCompressor:
    """对话压缩器"""

    def __init__(self, config: PlanExecuteConfig = default_config):
        self.config = config
        self.llm = ChatOpenAI(
            model=config.llm.model,
            temperature=0.2,
            api_key=config.llm.api_key,
            base_url=config.llm.base_url
        )
        self.max_messages = config.memory.max_messages_before_compress
        self.keep_recent = config.memory.keep_recent_messages

    async def compress_if_needed(
        self,
        messages: List[BaseMessage],
        existing_summary: str = ""
    ) -> tuple[str, List[BaseMessage]]:
        """
        如果消息数量超过阈值，压缩旧消息

        返回: (压缩后的摘要, 保留的最近消息)
        """
        if len(messages) <= self.max_messages:
            return existing_summary, messages

        # 分割：需要压缩的旧消息 + 保留的新消息
        messages_to_compress = messages[:-self.keep_recent]
        messages_to_keep = messages[-self.keep_recent:]

        # 格式化需要压缩的对话
        conversation_text = self._format_messages(messages_to_compress)

        # 如果已有摘要，合并压缩
        if existing_summary:
            conversation_text = f"【之前的摘要】\n{existing_summary}\n\n【新增对话】\n{conversation_text}"

        # 调用 LLM 压缩
        prompt = COMPRESS_PROMPT.format(conversation=conversation_text)
        result = await self.llm.ainvoke([HumanMessage(content=prompt)])
        new_summary = result.content

        logger.info(f"对话已压缩: {len(messages_to_compress)} 条消息 → 摘要")

        return new_summary, messages_to_keep

    def _format_messages(self, messages: List[BaseMessage]) -> str:
        """格式化消息列表为文本"""
        lines = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "用户"
            elif isinstance(msg, AIMessage):
                role = "助手"
            elif isinstance(msg, SystemMessage):
                role = "系统"
            else:
                role = "未知"
            lines.append(f"[{role}]: {msg.content[:500]}...")
        return "\n".join(lines)


# =========================================================
# 2. Mem0 记忆管理器
# =========================================================

class AgentMemory:
    """
    基于 Mem0 的 Agent 记忆管理器

    功能：
    1. 存储执行经验（成功/失败的方案）
    2. 检索相关记忆辅助决策
    3. 管理会话记忆
    """

    def __init__(self, config: PlanExecuteConfig = default_config):
        self.config = config
        self._memory = None
        self._initialized = False
        self.compressor = ConversationCompressor(config)

    async def initialize(self) -> bool:
        """
        异步初始化 Mem0

        注意：Mem0 初始化可能失败（如 Milvus 未启动），
        此时记忆功能降级为禁用状态
        """
        if not self.config.memory.enabled:
            logger.info("记忆系统已禁用")
            return False

        try:
            from mem0 import Memory

            mem0_config = self.config.memory.to_mem0_config(self.config.llm)
            self._memory = Memory.from_config(mem0_config)
            self._initialized = True
            logger.info("Mem0 记忆系统初始化成功")
            return True

        except ImportError:
            logger.warning("Mem0 未安装，记忆功能已禁用。请运行: pip install mem0ai")
            self._initialized = False
            return False

        except Exception as e:
            logger.warning(f"Mem0 初始化失败: {e}，记忆功能已禁用")
            self._initialized = False
            return False

    @property
    def is_available(self) -> bool:
        """记忆系统是否可用"""
        return self._initialized and self._memory is not None

    async def add(
        self,
        content: str,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        添加记忆

        Args:
            content: 记忆内容
            session_id: 会话 ID
            metadata: 附加元数据

        Returns:
            记忆 ID，失败返回 None
        """
        if not self.is_available:
            return None

        try:
            result = self._memory.add(
                content,
                user_id=session_id,
                metadata=metadata or {}
            )
            logger.debug(f"记忆已添加: {content[:50]}...")
            return result.get("id") if isinstance(result, dict) else None

        except Exception as e:
            logger.warning(f"添加记忆失败: {e}")
            return None

    async def search(
        self,
        query: str,
        session_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        搜索相关记忆

        Args:
            query: 查询内容
            session_id: 会话 ID
            limit: 返回数量上限

        Returns:
            相关记忆列表
        """
        if not self.is_available:
            return []

        try:
            results = self._memory.search(
                query,
                user_id=session_id,
                limit=limit
            )
            return results if isinstance(results, list) else []

        except Exception as e:
            logger.warning(f"搜索记忆失败: {e}")
            return []

    async def get_relevant_context(
        self,
        objective: str,
        session_id: str
    ) -> str:
        """
        获取与目标相关的记忆上下文

        Args:
            objective: 当前任务目标
            session_id: 会话 ID

        Returns:
            格式化的记忆上下文字符串
        """
        memories = await self.search(objective, session_id, limit=3)

        if not memories:
            return "无相关历史记忆"

        lines = ["## 相关历史经验"]
        for i, mem in enumerate(memories, 1):
            content = mem.get("memory", mem.get("content", ""))
            lines.append(f"{i}. {content}")

        return "\n".join(lines)

    async def store_execution_result(
        self,
        session_id: str,
        objective: str,
        plan_summary: str,
        success: bool,
        key_insights: str
    ) -> None:
        """
        存储执行结果作为经验记忆

        Args:
            session_id: 会话 ID
            objective: 任务目标
            plan_summary: 计划摘要
            success: 是否成功
            key_insights: 关键洞察/经验
        """
        status = "成功" if success else "失败"
        content = f"任务「{objective}」执行{status}。方案：{plan_summary}。经验：{key_insights}"

        await self.add(
            content=content,
            session_id=session_id,
            metadata={
                "type": "execution_result",
                "success": success,
                "objective_hash": hashlib.md5(objective.encode()).hexdigest()[:8]
            }
        )


# =========================================================
# 3. 便捷函数
# =========================================================

async def create_memory(config: PlanExecuteConfig = default_config) -> AgentMemory:
    """创建并初始化记忆管理器"""
    memory = AgentMemory(config)
    await memory.initialize()
    return memory


def generate_session_id(user_input: str) -> str:
    """根据用户输入生成会话 ID"""
    import time
    content = f"{user_input}_{time.time()}"
    return hashlib.md5(content.encode()).hexdigest()[:16]
