## MAS架构

可直接查阅官网，subagent、handoffs等有详细讲解和示例代码。



> 参考：[LangChain 多智能体架构：深入解析 Supervisor 与 Handoffs 模式](https://mp.weixin.qq.com/s/Os4K5IuRbWF6KGhv7DaKTA)，含示例代码辅助理解

多智能体系统通常采用两种协作范式：**集中编排的 “工具调用（Tool calling）”** （典型代表：主管模式：Supervisor）与**去中心化的 “交接（Handoffs）”**



主管模式（Supervisor Pattern）：

- 通过引入一个“总控智能体”来编排多个专业智能体，非常适用于跨角色分工的端到端流程。

  ```python
  math_agent = create_react_agent(
      model=model,
      tools=[add, multiply],
      name="math_expert",
      prompt="You are a math expert. Always use one tool at a time."
  )
  
  research_agent = create_react_agent(
      model=model,
      tools=[web_search],
      name="research_expert",
      prompt="You are a world class researcher with access to web search. Do not do any math."
  )
  
  # Create supervisor workflow
  workflow = create_supervisor(
      [research_agent, math_agent],
      model=model,
      prompt=(
          "You are a team supervisor managing a research expert and a math expert. "
          "For current events, use research_agent. "
          "For math problems, use math_agent."
      )
  )
  
  # Compile and run
  app = workflow.compile()
  result = app.invoke({
      "messages": [
          {
              "role": "user",
              "content": "what's the combined headcount of the FAANG companies in 2024?"
          }
      ]
  })
  ```

- 甚至，通过“主管管理主管”的方式，我们可以构建多级层级系统（Multi-level Hierarchies）。通过“顶层主管”来协调多个“子主管”

  ```python
  research_team = create_supervisor(
      [research_agent, math_agent],
      model=model,
      supervisor_name="research_supervisor"
  ).compile(name="research_team")
  
  writing_team = create_supervisor(
      [writing_agent, publishing_agent],
      model=model,
      supervisor_name="writing_supervisor"
  ).compile(name="writing_team")
  
  top_level_supervisor = create_supervisor(
      [research_team, writing_team],
      model=model,
      supervisor_name="top_level_supervisor"
  ).compile(name="top_level_supervisor")
  ```

  

Handoffs 交接：其工作流如下

1. 当前智能体判断需要其他角色的协助。
2. 它将控制权（以及当前状态）传递给下一个智能体。
3. 新的智能体接管对话，直接与用户交互，直到它决定再次交接或完成任务。



## 快速上手

### Plan-and-Execute

示例代码：

```python
"""
Plan-and-Execute 架构（LangGraph）
---------------------------------
1. Planner：生成 TODO 计划
2. Executor：逐条执行 TODO
3. Finalizer：汇总执行结果
"""

from typing import List, Tuple, Annotated
import operator
from typing_extensions import TypedDict
from dotenv import load_dotenv
import os

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

from app.prompt.planning import PLANNING_SYSTEM_PROMPT, EXECUTOR_SYSTEM_PROMPT

# =========================================================
# 1. 定义全局 State（Graph 状态）
# =========================================================

class PlanExecuteState(TypedDict):
    """
    input       : 用户原始目标
    plan        : TODO 清单
    past_steps  : 已执行步骤及结果
    response    : 最终输出
    """
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple[str, str]], operator.add]
    response: str


# =========================================================
# 2. Planner：生成 TODO 清单
# =========================================================

class Plan(BaseModel):
    steps: List[str] = Field(description="可执行的 TODO 步骤列表")


planner_prompt = ChatPromptTemplate.from_template(PLANNING_SYSTEM_PROMPT)

# 加载环境变量
load_dotenv(override=False)
model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    temperature=0.5,
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("BASE_URL")
)


planner_llm = model.with_structured_output(Plan)


def planner_node(state: PlanExecuteState) -> dict:
    """生成 TODO 计划"""
    result = planner_llm.invoke(
        planner_prompt.format_prompt(objective=state["input"])
    )
    return {"plan": result.steps}


# =========================================================
# 3. Executor：执行 TODO（逐条）
# =========================================================

executor_llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    temperature=0.5,
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("BASE_URL")
)


def executor_node(state: PlanExecuteState) -> dict:
    """
    每次执行 plan 中的第一个步骤
    """
    plan = state["plan"]

    if not plan:
        return {}

    # 取出下一步
    current_step = plan.pop(0)

    # 执行该步骤
    result = executor_llm.invoke(
        [
            ("system", EXECUTOR_SYSTEM_PROMPT),
            ("user", current_step),
        ]
    ).content

    return {
        "plan": plan,
        "past_steps": [(current_step, result)],
    }


# =========================================================
# 4. Finalizer：汇总结果
# =========================================================

def finalize_node(state: PlanExecuteState) -> dict:
    """汇总执行结果"""
    lines = ["## ✅ 执行结果汇总\n"]

    for idx, (step, result) in enumerate(state["past_steps"], start=1):
        lines.append(f"### Step {idx}: {step}")
        lines.append(result)
        lines.append("")

    return {"response": "\n".join(lines)}


# =========================================================
# 5. 构建 LangGraph
# =========================================================

graph = StateGraph(PlanExecuteState)

graph.add_node("planner", planner_node)
graph.add_node("executor", executor_node)
graph.add_node("finalizer", finalize_node)

# START → planner
graph.add_edge("__start__", "planner")

# planner → executor
graph.add_edge("planner", "executor")

# executor → executor / finalizer
graph.add_conditional_edges(
    "executor",
    lambda state: "continue" if state["plan"] else "end",
    {
        "continue": "executor",
        "end": "finalizer",
    },
)

# finalizer → END
graph.add_edge("finalizer", END)

app = graph.compile()



# =========================================================
# 6. 运行示例
# =========================================================

if __name__ == "__main__":
    user_input = "整理 2025 年机器学习的主要研究方向，并给出简要说明"

    result = app.invoke(
        {
            "input": user_input,
            "plan": [],
            "past_steps": [],
            "response": "",
        },
        config={"recursion_limit": 50},
    )

    print(result["response"])

```

