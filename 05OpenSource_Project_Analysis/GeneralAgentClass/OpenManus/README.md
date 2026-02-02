参考：

- https://www.bilibili.com/video/BV1SrRhYmEgm



新版本的上手比较慢，还是用老版本的好一点



OpenManus实现的功能相对来说比较简易，但是其代码框架写的很有学习价值



## Agent实现

OpenManus采用了层次化的代理结构，**通过继承关系实现功能的逐级扩展**：

- `BaseAgent`：所有代理的基类，定义基本状态和执行流程
- `ReActAgent(BaseAgent, ABC)`：实现思考-行动循环的代理基类
- `ToolCallAgent(ReActAgent)`：能够调用工具的代理实现
- `Manus(ToolCallAgent)`：最终的Manus代理，集成所有能力



## 工具设计

工具系统是OpenManus的核心功能组件，提供了与外部世界交互的能力：

- `BaseTool`：所有工具的基类，定义执行接口
- `ToolCollection`：工具管理类，负责工具注册和调用
- 具体工具实现：
- `BrowserUseTool`：浏览器交互工具
- `PythonExecute`：Python代码执行工具
- `GoogleSearch`：谷歌搜索工具
- `FileSaver`：文件保存工具
- `Terminate`：终止执行的工具



## PlanningFlow

### _create_initial_plan 详解
#### 1. 如何知道项目有哪些agent？
PlanningFlow 在初始化时会接收一个 agents 参数，这个参数可以是单个 BaseAgent 实例、 BaseAgent 列表或 Dict[str, BaseAgent] 字典。在 __init__ 方法中，这些 agents 会被存储在 self.agents 字典中，键为 agent 的名称，值为 agent 实例。 _create_initial_plan 方法通过访问 self.agents 和 self.executor_keys 来获取项目中的所有 agents 信息。

#### 2. 如何规划任务？
_create_initial_plan 方法使用 LLM 和 PlanningTool 来创建初始计划：

1. 1.构建系统提示 ：创建一个系统消息，告诉 LLM 它是一个规划助手，需要创建简洁、可操作的计划。如果存在多个 agents，还会在提示中包含这些 agents 的名称和描述，以便 LLM 在创建步骤时可以指定使用哪个 agent（通过 [agent_name] 格式）。
2. 2.构建用户提示 ：创建一个用户消息，其中包含用户请求的任务。
3. 3.调用 LLM ：使用 self.llm.ask_tool 方法，传入系统提示、用户提示和 PlanningTool ，让 LLM 生成一个计划。
4. 4.处理工具调用 ：如果 LLM 返回了工具调用（通常是 planning 工具），则解析参数并执行 PlanningTool 的相应命令（如 create ）来创建计划。
5. 5.默认计划 ：如果 LLM 没有返回有效的工具调用，则创建一个包含默认步骤（"Analyze request", "Execute task", "Verify results"）的计划。
#### 3. 执行任务时是顺序执行任务表吗？
是的，在 execute 方法中，任务是按顺序执行的：

1. 1.调用 _get_current_step_info 方法获取当前计划中第一个未完成的步骤。
2. 2.调用 get_executor 方法为该步骤选择合适的 agent。
3. 3.调用 _execute_step 方法使用选定的 agent 执行该步骤。
4. 4.重复上述过程，直到没有更多未完成的步骤。
#### 4. 计划中的不同步骤会涉及不同 Agent 吗？
会的， PlanningFlow 支持为不同步骤使用不同的 Agent：

1. 1.步骤类型指定 ：在创建计划时，可以在步骤描述中使用 [agent_name] 格式来指定该步骤应由哪个 agent 执行。
2. 2.执行器选择 ：在 get_executor 方法中，会检查步骤信息中的 type 字段（即从步骤描述中提取的 agent_name），如果存在且匹配某个 agent 的键，则返回该 agent。否则，按照 executor_keys 列表中的顺序返回第一个可用的 agent。
#### 5. 步骤失败多次会有终止机制吗？
源码中没有明确的步骤失败次数限制和自动终止机制。当前的错误处理主要体现在：

1. 1.步骤执行错误 ：在 _execute_step 方法中，如果执行步骤时发生异常，会记录错误日志并返回错误信息，但不会终止整个流程。流程会继续尝试执行下一个步骤。
2. 2.Agent 状态检查 ：在 execute 方法的主循环中，会检查当前执行 agent 的状态（ executor.state ），如果状态为 AgentState.FINISHED ，则会跳出循环，终止流程。这是由 agent 自身决定何时完成的机制。
3. 3.全局异常处理 ： execute 方法有一个全局的 try-except 块，捕获所有异常并返回错误信息，这会终止整个流程。
   虽然没有基于失败次数的自动终止，但可以通过在 agent 的实现中加入重试逻辑或失败处理策略来增强鲁棒性。



### Multi-Agent之间的上下文管理

经过对OpenManus项目中PlanningFlow及相关Agent实现的分析，我可以得出以下关于多Agent应用中上下文管理机制的结论：

1.**独立内存管理**：

- 每个Agent都有自己独立的Memory实例，存储其自身的消息历史和上下文 `base.py`
- Memory类包含消息列表、最大消息数量限制以及相关管理方法 `schema.py`

2.**上下文共享机制**：

- 在PlanningFlow中，不同Agent之间**不共享全部上下文**，而是采用有选择性的上下文传递机制
- 当执行特定步骤时，PlanningFlow通过_execute_step方法将当前计划状态作为上下文传递给执行该步骤的Agent `planning.py`
- 具体实现方式是创建一个包含当前计划状态的提示文本，然后将其作为参数传递给Agent的run方法

3.**选择性信息传递**：

- PlanningFlow根据步骤类型选择合适的Agent执行任务 (get_executor方法)
- 在执行每个步骤时，会将当前计划状态、进度和任务详情传递给负责执行的Agent
- 但Agent的内部状态（如完整的消息历史）不会自动共享给其他Agent

4.**协调机制**：

- PlanningFlow作为中央协调器，负责创建计划、分配任务、收集结果
- 通过PlanningTool管理计划状态，所有Agent通过这个中央工具可以访问任务相关的上下文信息

这种设计允许每个Agent在执行特定任务时获得必要的上下文，同时保持各自独立的内部状态，避免信息过载和潜在的上下文混淆。

