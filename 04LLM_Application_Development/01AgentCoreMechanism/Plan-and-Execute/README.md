架构示意图：

```py
                    ┌──────────────┐
                    │   __start__  │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │    Planner   │ ← 检索相关记忆
                    │   (async)    │
                    └──────┬───────┘
                           │
              ┌────────────▼────────────┐
              │        Executor         │ ← MCP 工具调用
              │  (async + tool_call)    │
              └────────────┬────────────┘
                           │
                    ┌──────▼───────┐
                    │    Judge     │
                    │   (async)    │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐   ┌──────▼──────┐   ┌─────▼─────┐
    │ continue  │   │   replan    │   │    end    │
    │ (executor)│   │ (replanner) │   │(finalizer)│
    └───────────┘   └─────────────┘   └─────┬─────┘
                                            │
                                    ┌───────▼───────┐
                                    │   Finalizer   │ ← 存储到记忆
                                    │    (async)    │
                                    └───────┬───────┘
                                            │
                                    ┌───────▼───────┐
                                    │      END      │
                                    └───────────────┘
```

示例结果：

```bash
$ python -m app.agent.standard_plan_execute
============================================================
🎉 最终结果
============================================================
# Python与Go并发编程综合分析与选型建议
......

============================================================
📊 执行统计
============================================================
  total_steps: 5
  successful_steps: 5
  failed_steps: 0
  replan_count: 0
  plan_version: 1
  success: True
```



## State 设计思想

### 1、单一事实源

`StandardPlanExecuteState` 是 Planner / Executor / Judge / Replanner / Finalizer 的唯一上下文载体。

LangGraph 保证：

- 每个节点 **读取同一个 State**
- 节点返回的是 **对 State 的增量更新**
- Graph 自动 merge

```python
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
```



### 2、模块间上下文流动总图

```bash
┌─────────────┐
│ Global State│  ← 单一共享
└─────┬───────┘
      │
Planner
  ├─ read: original_input, tools, memory_context
  └─ write: current_plan, plan_version

Executor
  ├─ read: current_plan, execution_history, shared_context
  └─ write: execution_history, shared_context, last_execution_status

Judge
  ├─ read: execution_history, last_execution_status, current_plan
  └─ write: judge_decision

Replanner
  ├─ read: execution_history, shared_context, current_plan
  └─ write: current_plan, execution_history(trim), replan_count

Finalizer
  ├─ read: execution_history, original_input
  └─ write: final_response, metadata, memory

```



### 3、State 按“层次”拆解

你的 State 设计其实已经天然分层了 👇

🧩 1. 用户输入层（Immutable / 只读）

```python
original_input: str
session_id: str
```

**特点：**

- Planner / Executor / Judge / Replanner / Finalizer 全部可读
- ❌ 从不修改

**作用：**

- 全流程的“北极星目标”
- Judge / Replanner 判断是否偏离目标

------

🧠 2. 规划层（Planner 主写，其它读）

```
current_plan: List[Dict]
plan_version: int
```

| 模块      | 行为              |
| --------- | ----------------- |
| Planner   | ✅ 写              |
| Replanner | ✅ 写（替换/调整） |
| Executor  | 👀 读              |
| Judge     | 👀 读              |
| Finalizer | 👀 读              |

**关键点：**

- `plan_version` 是**计划的世代号**
- Replan 不是“打补丁”，而是**产生新版本计划**

👉 非常适合审计 & Debug。

------

⚙️ 3. 执行层（Executor 主写）

```python
execution_history: List[ExecutionRecord]
current_step_index: int
last_execution_status: str
```

| 模块      | 行为 |
| --------- | ---- |
| Executor  | ✅ 写 |
| Judge     | 👀 读 |
| Replanner | 👀 读 |
| Finalizer | 👀 读 |

**这是最核心的“运行时上下文”**

- `execution_history` = **事实日志**
- Judge **不依赖 LLM 记忆，只依赖执行事实**
- Replanner **只基于成功/失败记录重建计划**

👉 这是“Plan-and-Execute 不会失控”的关键。

------

🔧 4. 工具层（初始化写，其它只读）

```python
tools: List[BaseTool]
tools_description: str
```

- 初始化阶段写
- Planner / Executor 只读

**设计亮点：**

- Planner 是 *tool-aware*
- Executor 是 *tool-capable*
- Judge / Replanner 完全不碰工具

👉 职责边界非常清晰。

------

🔄 5. 共享上下文层（Executor 主写，全体读）

```python
shared_context: Dict[str, Any]
```

这是你这个架构里**最“Agent 化”的设计**。

**特点：**

- Executor 在每一步：

  ```python
  shared_context = old + result.shared_updates
  ```

- Planner 不直接写

- Replanner 会基于它进行决策

- Finalizer 用它做最终总结

👉 它的角色是：

> **“跨步骤的结构化黑板（Blackboard）”**

这比把信息塞进自然语言 history 要强得多。

------

🧠 6. 记忆层（只在边缘节点交互）

```
memory_context: str
compressed_history: str
```

**设计哲学非常克制：**

| 阶段      | 行为             |
| --------- | ---------------- |
| Planner   | 👀 读（辅助规划） |
| Executor  | ❌ 不读           |
| Judge     | ❌ 不读           |
| Replanner | ❌ 不读           |
| Finalizer | ✅ 写（存经验）   |

👉 记忆是：

- **规划的背景**
- **执行后的沉淀**
- ❌ 不是每一步的隐式上下文

这是非常正确的。

------

⚖️ 7. 判断与控制层（Judge / Replanner）

```python
judge_decision: str
replan_reason: Optional[str]
replan_count: int
```

这是**防止 Agent 失控的安全带**：

- Judge：只写 `judge_decision`
- Replanner：写 `replan_count` / `replan_reason`
- Graph routing **只读 State，不再调用 LLM**

👉 这是你代码里一个**非常重要的成熟设计点**。

------

📝 8. 输出层（Finalizer 独占）

```python
final_response: str
metadata: Dict[str, Any]
```

- 所有节点都不碰
- Finalizer 一次性写

👉 输出与执行逻辑彻底解耦
