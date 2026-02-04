"""
标准 Plan-and-Execute 架构（LangGraph 异步实现）
=================================================
包含模块：
1. Planner：生成结构化执行计划（支持工具感知）
2. Executor：带工具调用能力的执行器
3. Judge：判断是否需要 Replan
4. Replanner：动态调整计划
5. Finalizer：汇总最终结果
6. Memory：基于 Mem0 的记忆系统

核心特性：
- ✅ 异步执行
- ✅ MCP 工具集成
- ✅ 步骤间依赖管理
- ✅ 共享上下文传递
- ✅ 执行历史追踪
- ✅ 失败自动重规划
- ✅ 防止无限循环
- ✅ 记忆系统支持
"""

import json
import time
import logging
from typing import List, Dict, Any, Optional, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END

from app.agent.config import PlanExecuteConfig, default_config
from app.agent.memory import AgentMemory, create_memory, generate_session_id
from app.prompt.planning import (
    TOOL_ENHANCED_PLANNER_PROMPT,
    TOOL_ENHANCED_EXECUTOR_PROMPT,
    JUDGE_PROMPT,
    REPLANNER_PROMPT,
    FINALIZER_PROMPT,
    TOOL_SELECTOR_PROMPT,
    EXPERIENCE_SUMMARY_PROMPT
)

logger = logging.getLogger(__name__)


# =========================================================
# 1. 数据结构定义
# =========================================================

class PlanStep(BaseModel):
    """单个计划步骤"""
    step_id: str = Field(description="步骤唯一ID")
    description: str = Field(description="步骤描述")
    expected_output: str = Field(description="期望输出类型")
    dependencies: List[str] = Field(default=[], description="依赖的前置步骤ID")
    suggested_tools: List[str] = Field(default=[], description="建议使用的工具")


class ExecutionRecord(BaseModel):
    """执行记录"""
    step_id: str = Field(description="对应的步骤ID")
    input_snapshot: Dict[str, Any] = Field(default={}, description="执行时的输入快照")
    output: str = Field(description="执行结果")
    status: str = Field(description="success/failed/skipped")
    tool_calls: List[Dict[str, Any]] = Field(default=[], description="工具调用记录")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    timestamp: float = Field(default_factory=time.time, description="执行时间戳")


class PlannerOutput(BaseModel):
    """Planner 结构化输出"""
    steps: List[PlanStep] = Field(description="执行步骤列表")


class ExecutorOutput(BaseModel):
    """Executor 结构化输出"""
    action: Literal["tool_call", "direct_response"] = Field(description="动作类型")
    tool_name: Optional[str] = Field(default=None, description="工具名称")
    tool_input: Optional[Dict[str, Any]] = Field(default=None, description="工具参数")
    result: Optional[str] = Field(default=None, description="直接响应结果")
    shared_updates: Dict[str, Any] = Field(default={}, description="共享上下文更新")
    status: str = Field(default="success", description="执行状态")
    error_message: Optional[str] = Field(default=None, description="错误信息")


class JudgeOutput(BaseModel):
    """Judge 结构化输出"""
    decision: Literal["CONTINUE", "REPLAN", "END"] = Field(description="判断结果")
    reason: str = Field(description="判断理由")


class ReplannerOutput(BaseModel):
    """Replanner 结构化输出"""
    reuse_steps: List[str] = Field(description="可复用的步骤ID")
    new_steps: List[PlanStep] = Field(description="新的执行步骤")
    adjustment_summary: str = Field(description="调整说明")


class StandardPlanExecuteState(TypedDict):
    """标准 Plan-and-Execute 架构的全局 State"""

    # ============ 用户输入层 ============
    original_input: str              # 用户原始目标（不可变）
    session_id: str                  # 会话 ID

    # ============ 规划层 ============
    current_plan: List[Dict[str, Any]]  # 当前执行计划
    plan_version: int                # 计划版本号

    # ============ 执行层 ============
    execution_history: List[Dict[str, Any]]  # 完整执行历史
    current_step_index: int          # 当前执行到第几步

    # ============ 工具层 ============
    tools: List[BaseTool]            # 可用工具列表
    tools_description: str           # 工具描述文本

    # ============ 上下文共享层 ============
    shared_context: Dict[str, Any]   # 步骤间共享的数据

    # ============ 记忆层 ============
    memory_context: str              # 检索到的相关记忆
    compressed_history: str          # 压缩后的对话历史

    # ============ 判断与反馈层 ============
    last_execution_status: str       # 上次执行状态
    judge_decision: str              # Judge 的判断结果
    replan_reason: Optional[str]     # 触发 Replan 的原因
    replan_count: int                # Replan 次数（防止无限循环）

    # ============ 输出层 ============
    final_response: str              # 最终输出
    metadata: Dict[str, Any]         # 元数据


# =========================================================
# 2. 工具管理
# =========================================================

async def load_mcp_tools(config: PlanExecuteConfig) -> tuple[List[BaseTool], str]:
    """
    加载 MCP 工具

    Returns:
        (工具列表, 工具描述文本)
    """
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient

        client_config = config.mcp.to_client_config()
        client = MultiServerMCPClient(client_config)

        tools = await client.get_tools()
        logger.info(f"已加载 {len(tools)} 个 MCP 工具")

        # 生成工具描述
        descriptions = []
        for tool in tools:
            desc = f"- **{tool.name}**: {tool.description}"
            descriptions.append(desc)

        tools_description = "\n".join(descriptions) if descriptions else "无可用工具"

        return tools, tools_description

    except Exception as e:
        logger.warning(f"MCP 工具加载失败: {e}，将以无工具模式运行")
        return [], "无可用工具（MCP 连接失败）"


def format_tools_for_prompt(tools: List[BaseTool]) -> str:
    """格式化工具信息用于 Prompt"""
    if not tools:
        return "无可用工具"

    lines = []
    for tool in tools:
        lines.append(f"- **{tool.name}**: {tool.description}")
        # 如果有参数 schema，也可以添加
    return "\n".join(lines)


# =========================================================
# 3. LLM 工厂
# =========================================================

def get_llm(config: PlanExecuteConfig, temperature: float = 0.3):
    """获取 LLM 实例"""
    return ChatOpenAI(
        model=config.llm.model,
        temperature=temperature,
        api_key=config.llm.api_key,
        base_url=config.llm.base_url
    )


# =========================================================
# 4. Planner 节点（异步）
# =========================================================

async def planner_node(
    state: StandardPlanExecuteState,
    config: PlanExecuteConfig = default_config
) -> Dict[str, Any]:
    """
    生成初始执行计划（工具感知版本）
    """
    logger.info("🧠 [Planner] 正在生成执行计划...")

    llm = get_llm(config, temperature=0.3).with_structured_output(PlannerOutput)

    prompt = TOOL_ENHANCED_PLANNER_PROMPT.format(
        objective=state["original_input"],
        available_tools=state.get("tools_description", "无可用工具"),
        memory_context=state.get("memory_context", "无相关历史记忆")
    )

    result = await llm.ainvoke([HumanMessage(content=prompt)])

    # 将 Pydantic 对象转换为 dict
    plan_dicts = [step.model_dump() for step in result.steps]

    logger.info(f"✅ [Planner] 已生成 {len(plan_dicts)} 个步骤")
    for i, step in enumerate(plan_dicts, 1):
        tools_hint = f" (工具: {', '.join(step['suggested_tools'])})" if step['suggested_tools'] else ""
        logger.info(f"   {i}. [{step['step_id']}] {step['description']}{tools_hint}")

    return {
        "current_plan": plan_dicts,
        "plan_version": state["plan_version"] + 1,
        "current_step_index": 0
    }


# =========================================================
# 5. Executor 节点（异步 + 工具调用）
# =========================================================

def format_plan_overview(plan: List[Dict[str, Any]]) -> str:
    """格式化计划概览"""
    lines = []
    for i, step in enumerate(plan, 1):
        deps = ", ".join(step["dependencies"]) if step["dependencies"] else "无"
        tools = ", ".join(step.get("suggested_tools", [])) or "无"
        lines.append(f"{i}. [{step['step_id']}] {step['description']} (依赖: {deps}, 工具: {tools})")
    return "\n".join(lines)


def get_dependency_results(
    step: Dict[str, Any],
    execution_history: List[Dict[str, Any]]
) -> str:
    """获取依赖步骤的执行结果"""
    if not step["dependencies"]:
        return "无前置步骤"

    lines = []
    for dep_id in step["dependencies"]:
        record = next(
            (r for r in execution_history if r["step_id"] == dep_id),
            None
        )
        if record:
            lines.append(f"[{dep_id}]:")
            lines.append(record["output"])
            lines.append("")

    return "\n".join(lines) if lines else "依赖步骤未找到执行记录"


async def execute_tool(
    tool_name: str,
    tool_input: Dict[str, Any],
    tools: List[BaseTool]
) -> tuple[str, bool]:
    """
    执行工具调用

    Returns:
        (结果文本, 是否成功)
    """
    tool = next((t for t in tools if t.name == tool_name), None)

    if not tool:
        return f"工具 '{tool_name}' 不存在", False

    try:
        result = await tool.ainvoke(tool_input)
        return str(result), True
    except Exception as e:
        return f"工具执行失败: {str(e)}", False


async def executor_node(
    state: StandardPlanExecuteState,
    config: PlanExecuteConfig = default_config
) -> Dict[str, Any]:
    """
    执行当前步骤（支持工具调用）
    """
    current_index = state["current_step_index"]
    current_step = state["current_plan"][current_index]

    logger.info(
        f"⚙️  [Executor] 执行步骤 {current_index + 1}/{len(state['current_plan'])}: "
        f"[{current_step['step_id']}] {current_step['description']}"
    )

    llm = get_llm(config, temperature=0.5).with_structured_output(ExecutorOutput)

    # 构造执行 Prompt
    prompt = TOOL_ENHANCED_EXECUTOR_PROMPT.format(
        objective=state["original_input"],
        plan_overview=format_plan_overview(state["current_plan"]),
        current_step_id=current_step["step_id"],
        current_step_description=current_step["description"],
        expected_output=current_step["expected_output"],
        suggested_tools=", ".join(current_step.get("suggested_tools", [])) or "无",
        dependency_results=get_dependency_results(current_step, state["execution_history"]),
        shared_context=json.dumps(state["shared_context"], ensure_ascii=False, indent=2),
        available_tools=state.get("tools_description", "无可用工具")
    )

    tool_calls = []

    try:
        result = await llm.ainvoke([HumanMessage(content=prompt)])

        # 处理工具调用
        if result.action == "tool_call" and result.tool_name:
            logger.info(f"🔧 [Executor] 调用工具: {result.tool_name}")

            tool_result, tool_success = await execute_tool(
                result.tool_name,
                result.tool_input or {},
                state.get("tools", [])
            )

            tool_calls.append({
                "tool_name": result.tool_name,
                "tool_input": result.tool_input,
                "tool_output": tool_result,
                "success": tool_success
            })

            output = tool_result
            status = "success" if tool_success else "failed"
            error_msg = None if tool_success else tool_result

        else:
            # 直接响应
            output = result.result or ""
            status = result.status
            error_msg = result.error_message

        # 创建执行记录
        execution_record = {
            "step_id": current_step["step_id"],
            "input_snapshot": {
                "description": current_step["description"],
                "dependencies": current_step["dependencies"]
            },
            "output": output,
            "status": status,
            "tool_calls": tool_calls,
            "error_message": error_msg,
            "timestamp": time.time()
        }

        # 更新共享上下文
        updated_context = {**state["shared_context"], **result.shared_updates}

        status_icon = "✅" if status == "success" else "❌"
        logger.info(f"{status_icon} [Executor] 步骤 {current_step['step_id']} 执行{status}")

        return {
            "execution_history": state["execution_history"] + [execution_record],
            "shared_context": updated_context,
            "current_step_index": current_index + 1,
            "last_execution_status": status
        }

    except Exception as e:
        logger.error(f"❌ [Executor] 步骤 {current_step['step_id']} 执行异常: {str(e)}")

        execution_record = {
            "step_id": current_step["step_id"],
            "input_snapshot": {},
            "output": "",
            "status": "failed",
            "tool_calls": tool_calls,
            "error_message": str(e),
            "timestamp": time.time()
        }

        return {
            "execution_history": state["execution_history"] + [execution_record],
            "current_step_index": current_index + 1,
            "last_execution_status": "failed"
        }


# =========================================================
# 6. Judge 节点（异步）
# =========================================================

async def judge_node(
    state: StandardPlanExecuteState,
    config: PlanExecuteConfig = default_config
) -> Dict[str, Any]:
    """
    判断下一步行动，将判断结果存入 state
    """
    logger.info("⚖️  [Judge] 评估当前执行状态...")

    # 1. 检查是否完成所有步骤
    if state["current_step_index"] >= len(state["current_plan"]):
        logger.info("✅ [Judge] 所有步骤已完成 → END")
        return {"judge_decision": "end"}

    # 2. 检查是否达到 Replan 上限
    max_replan = config.max_replan_count
    if state["replan_count"] >= max_replan:
        logger.warning(f"⚠️  [Judge] 已达到最大 Replan 次数 ({max_replan}) → END")
        return {"judge_decision": "end"}

    # 3. 如果最后一步失败，调用 LLM 判断
    if state["last_execution_status"] == "failed":
        logger.info("⚠️  [Judge] 检测到步骤失败，调用 LLM 判断...")

        llm = get_llm(config, temperature=0.2).with_structured_output(JudgeOutput)

        last_record = state["execution_history"][-1] if state["execution_history"] else {}

        prompt = JUDGE_PROMPT.format(
            objective=state["original_input"],
            current_plan=format_plan_overview(state["current_plan"]),
            execution_history="\n".join([
                f"[{r['step_id']}] {r['status']}: {r['output'][:100]}..."
                for r in state["execution_history"]
            ]),
            completed_count=len([r for r in state["execution_history"] if r["status"] == "success"]),
            total_count=len(state["current_plan"]),
            last_status=last_record.get("status", "unknown")
        )

        try:
            result = await llm.ainvoke([HumanMessage(content=prompt)])
            decision = result.decision.lower()

            logger.info(f"🤔 [Judge] LLM 判断: {result.decision}")
            logger.info(f"   理由: {result.reason}")

            return {"judge_decision": decision}

        except Exception as e:
            logger.warning(f"⚠️  [Judge] LLM 判断异常: {e}，默认继续执行")

    # 4. 默认继续执行
    logger.info("➡️  [Judge] 继续执行下一步 → CONTINUE")
    return {"judge_decision": "continue"}


def route_after_judge(state: StandardPlanExecuteState) -> str:
    """
    Judge 后的路由函数（只读取 state，不重复调用 judge_node）
    """
    return state.get("judge_decision", "continue")


# =========================================================
# 7. Replanner 节点（异步）
# =========================================================

async def replanner_node(
    state: StandardPlanExecuteState,
    config: PlanExecuteConfig = default_config
) -> Dict[str, Any]:
    """
    重新规划（保留成功步骤的完整信息）
    """
    logger.info(f"🔄 [Replanner] 开始重新规划（第 {state['replan_count'] + 1} 次）...")

    llm = get_llm(config, temperature=0.4).with_structured_output(ReplannerOutput)

    # 获取成功的步骤
    completed_steps = [
        r for r in state["execution_history"]
        if r["status"] == "success"
    ]
    completed_step_ids = [r["step_id"] for r in completed_steps]

    # 获取失败信息
    last_failed = next(
        (r for r in reversed(state["execution_history"]) if r["status"] == "failed"),
        None
    )
    failure_info = (
        f"步骤 [{last_failed['step_id']}] 失败: {last_failed.get('error_message', '未知错误')}"
        if last_failed else "未知失败"
    )

    prompt = REPLANNER_PROMPT.format(
        objective=state["original_input"],
        plan_version=state["plan_version"],
        old_plan=format_plan_overview(state["current_plan"]),
        completed_steps="\n".join([
            f"[{r['step_id']}]: {r['output'][:100]}..."
            for r in completed_steps
        ]) or "无已完成步骤",
        failure_info=failure_info,
        shared_context=json.dumps(state["shared_context"], ensure_ascii=False, indent=2)
    )

    try:
        result = await llm.ainvoke([HumanMessage(content=prompt)])

        # 保留可复用步骤的执行记录
        retained_history = [
            r for r in state["execution_history"]
            if r["step_id"] in result.reuse_steps
        ]

        # 构建新计划：复用的旧步骤 + 新步骤
        # 从旧计划中提取被复用步骤的完整定义
        reused_step_defs = [
            step for step in state["current_plan"]
            if step["step_id"] in result.reuse_steps
        ]

        # 新步骤转换为 dict
        new_step_defs = [step.model_dump() for step in result.new_steps]

        # 合并计划
        new_plan = reused_step_defs + new_step_defs

        logger.info(f"✅ [Replanner] 新计划已生成:")
        logger.info(f"   - 复用步骤: {', '.join(result.reuse_steps) or '无'}")
        logger.info(f"   - 新增步骤: {len(new_step_defs)} 个")
        logger.info(f"   - 调整说明: {result.adjustment_summary}")

        return {
            "current_plan": new_plan,
            "plan_version": state["plan_version"] + 1,
            "execution_history": retained_history,
            "current_step_index": len(retained_history),
            "replan_count": state["replan_count"] + 1,
            "replan_reason": result.adjustment_summary,
            "last_execution_status": "success",
            "judge_decision": ""  # 清空判断结果
        }

    except Exception as e:
        logger.error(f"❌ [Replanner] 重新规划失败: {e}")
        # 如果 Replan 失败，直接结束
        return {
            "current_step_index": len(state["current_plan"]),
            "judge_decision": "end"
        }


# =========================================================
# 8. Finalizer 节点（异步 + 记忆存储）
# =========================================================

async def finalizer_node(
    state: StandardPlanExecuteState,
    config: PlanExecuteConfig = default_config,
    memory: Optional[AgentMemory] = None
) -> Dict[str, Any]:
    """
    汇总最终结果并存储执行经验
    """
    logger.info("📝 [Finalizer] 汇总最终结果...")

    llm = get_llm(config, temperature=0.3)

    # 格式化执行历史
    history_text = []
    for i, record in enumerate(state["execution_history"], 1):
        status_icon = "✅" if record["status"] == "success" else "❌"
        history_text.append(f"{status_icon} Step {i} [{record['step_id']}]:")
        history_text.append(record["output"])
        if record.get("tool_calls"):
            for tc in record["tool_calls"]:
                history_text.append(f"   🔧 工具调用: {tc['tool_name']}")
        history_text.append("")

    prompt = FINALIZER_PROMPT.format(
        objective=state["original_input"],
        execution_history="\n".join(history_text)
    )

    result = await llm.ainvoke([HumanMessage(content=prompt)])

    # 计算元数据
    successful_steps = len([r for r in state["execution_history"] if r["status"] == "success"])
    failed_steps = len([r for r in state["execution_history"] if r["status"] == "failed"])
    total_steps = len(state["execution_history"])
    success = failed_steps == 0

    metadata = {
        "total_steps": total_steps,
        "successful_steps": successful_steps,
        "failed_steps": failed_steps,
        "replan_count": state["replan_count"],
        "plan_version": state["plan_version"],
        "success": success
    }

    # 存储执行经验到记忆系统
    if memory and memory.is_available:
        try:
            # 生成经验总结
            summary_prompt = EXPERIENCE_SUMMARY_PROMPT.format(
                objective=state["original_input"],
                plan_summary=format_plan_overview(state["current_plan"])[:500],
                execution_result=result.content[:500],
                success="成功" if success else "失败"
            )
            summary_result = await llm.ainvoke([HumanMessage(content=summary_prompt)])

            await memory.store_execution_result(
                session_id=state.get("session_id", "default"),
                objective=state["original_input"],
                plan_summary=format_plan_overview(state["current_plan"])[:200],
                success=success,
                key_insights=summary_result.content
            )
            logger.info("💾 [Finalizer] 执行经验已存储到记忆系统")

        except Exception as e:
            logger.warning(f"⚠️  [Finalizer] 存储执行经验失败: {e}")

    logger.info("✅ [Finalizer] 结果汇总完成")

    return {
        "final_response": result.content,
        "metadata": metadata
    }


# =========================================================
# 9. 构建 LangGraph（异步版本）
# =========================================================

def create_standard_plan_execute_graph(
    config: PlanExecuteConfig = default_config,
    memory: Optional[AgentMemory] = None
):
    """
    创建标准 Plan-and-Execute 工作流（异步版本）
    """
    graph = StateGraph(StandardPlanExecuteState)

    # 创建绑定配置的节点函数
    async def _planner(state):
        return await planner_node(state, config)

    async def _executor(state):
        return await executor_node(state, config)

    async def _judge(state):
        return await judge_node(state, config)

    async def _replanner(state):
        return await replanner_node(state, config)

    async def _finalizer(state):
        return await finalizer_node(state, config, memory)

    # 添加节点
    graph.add_node("planner", _planner)
    graph.add_node("executor", _executor)
    graph.add_node("judge", _judge)
    graph.add_node("replanner", _replanner)
    graph.add_node("finalizer", _finalizer)

    # 定义边
    graph.add_edge("__start__", "planner")
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "judge")

    # Judge 的条件分支（修复：使用路由函数而非重复调用 judge_node）
    graph.add_conditional_edges(
        "judge",
        route_after_judge,
        {
            "continue": "executor",
            "replan": "replanner",
            "end": "finalizer"
        }
    )

    # Replanner → Executor
    graph.add_edge("replanner", "executor")

    # Finalizer → END
    graph.add_edge("finalizer", END)

    return graph.compile()


# =========================================================
# 10. 高级 API
# =========================================================

class StandardPlanExecuteAgent:
    """
    标准 Plan-and-Execute Agent 封装类

    提供简洁的 API 来运行 Agent
    """

    def __init__(self, config: PlanExecuteConfig = default_config):
        self.config = config
        self.memory: Optional[AgentMemory] = None
        self.tools: List[BaseTool] = []
        self.tools_description: str = "无可用工具"
        self._graph = None
        self._initialized = False

    async def initialize(self) -> "StandardPlanExecuteAgent":
        """
        异步初始化 Agent（加载工具和记忆系统）
        """
        if self._initialized:
            return self

        # 加载 MCP 工具
        self.tools, self.tools_description = await load_mcp_tools(self.config)

        # 初始化记忆系统
        self.memory = await create_memory(self.config)

        # 创建图
        self._graph = create_standard_plan_execute_graph(self.config, self.memory)

        self._initialized = True
        logger.info("🚀 StandardPlanExecuteAgent 初始化完成")

        return self

    async def run(
        self,
        user_input: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        运行 Agent

        Args:
            user_input: 用户输入的目标
            session_id: 会话 ID（可选，自动生成）

        Returns:
            执行结果字典
        """
        if not self._initialized:
            await self.initialize()

        session_id = session_id or generate_session_id(user_input)

        # 获取相关记忆
        memory_context = "无相关历史记忆"
        if self.memory and self.memory.is_available:
            memory_context = await self.memory.get_relevant_context(
                user_input,
                session_id
            )

        # 构造初始状态
        initial_state: StandardPlanExecuteState = {
            "original_input": user_input,
            "session_id": session_id,
            "current_plan": [],
            "plan_version": 0,
            "execution_history": [],
            "current_step_index": 0,
            "tools": self.tools,
            "tools_description": self.tools_description,
            "shared_context": {},
            "memory_context": memory_context,
            "compressed_history": "",
            "last_execution_status": "success",
            "judge_decision": "",
            "replan_reason": None,
            "replan_count": 0,
            "final_response": "",
            "metadata": {}
        }

        logger.info("=" * 60)
        logger.info("🚀 标准 Plan-and-Execute Agent 启动")
        logger.info("=" * 60)
        logger.info(f"📌 用户目标: {user_input}")
        logger.info(f"🔧 可用工具: {len(self.tools)} 个")
        logger.info(f"💾 记忆系统: {'可用' if self.memory and self.memory.is_available else '不可用'}")

        # 运行图
        result = await self._graph.ainvoke(
            initial_state,
            config={"recursion_limit": self.config.recursion_limit}
        )

        logger.info("\n" + "=" * 60)
        logger.info("🎉 执行完成")
        logger.info("=" * 60)

        return result


# =========================================================
# 11. 便捷函数
# =========================================================

async def run_plan_execute(
    user_input: str,
    config: Optional[PlanExecuteConfig] = None
) -> Dict[str, Any]:
    """
    便捷函数：运行 Plan-and-Execute Agent
    """
    agent = StandardPlanExecuteAgent(config or default_config)
    return await agent.run(user_input)


# =========================================================
# 12. 运行示例
# =========================================================

if __name__ == "__main__":
    import asyncio

    async def main():
        user_input = "分析 Python 和 Go 语言在并发编程方面的优劣，并给出选型建议"

        agent = StandardPlanExecuteAgent()
        result = await agent.run(user_input)

        print("\n" + "=" * 60)
        print("🎉 最终结果")
        print("=" * 60)
        print(result["final_response"])

        print("\n" + "=" * 60)
        print("📊 执行统计")
        print("=" * 60)
        for key, value in result["metadata"].items():
            print(f"  {key}: {value}")

    asyncio.run(main())
