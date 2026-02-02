TODO：

- [LangGraph+DAG 最佳实践：DeerFlow如何用有向无环图实现高效工作流编排？](https://mp.weixin.qq.com/s/XPwYosWxxPLyN3TDaS2Mhw)



## Multi-Agent之间的上下文管理

通过对 deer-flow 项目源码的分析，我发现该项目中不同 Agent 之间 共享全部上下文 ，主要通过以下机制实现：

### 1. 统一的状态对象设计
项目使用了 State 类（ `types.py` ）作为所有 Agent 之间共享信息的核心载体。这个类继承自 langgraph.graph.MessagesState ，并扩展了多个字段来存储不同类型的上下文信息：

```
class State(MessagesState):
    # Runtime Variables
    locale: str = "en-US"
    research_topic: str = ""
    observations: list[str] = []
    resources: list[Resource] = []
    plan_iterations: int = 0
    current_plan: Plan | str = None
    final_report: str = ""
    # 其他字段...
```
### 2. 基于 langgraph 的状态管理
项目使用 langgraph 库构建状态图（ `builder.py` ），所有 Agent 节点都操作同一个状态对象：

```
def _build_base_graph():
    builder = StateGraph(State)
    builder.add_edge(START, "coordinator")
    # 添加其他节点和边...
```
### 3. 上下文共享的具体实现
在 `nodes.py` 中，各个节点通过 Command 对象更新状态并传递信息：

1.完整历史记录共享 ：通过 observations 列表存储所有 Agent 的执行结果

2.步骤信息传递 ：在 _execute_agent_step 函数中，会将已完成步骤的信息包含在当前 Agent 的输入中

3.记忆机制 ：通过 MemorySaver 实现对话历史的持久化存储

### 4. Agent 协作流程
各 Agent 协作时遵循以下上下文共享模式：

1.所有 Agent 可以读取整个状态对象中的信息

2.每个 Agent 完成工作后，通过 Command(update=...) 更新状态

3.更新的状态会被传递给下一个执行的 Agent

4.Agent 可以访问之前所有 Agent 的工作成果

### 结论
在 deer-flow 项目中，不同 Agent 之间确实共享全部上下文。这种设计使得多个 Agent 能够协同完成复杂任务，每个 Agent 都能基于全局信息做出决策，而不仅仅依赖于局部信息。



## 上下文工程

经过对 deer-flow/src 目录下源码的分析，我发现该项目确实涉及一些上下文工程的实现，但主要集中在以下几个方面：

#### 1. 文本压缩和扩展功能
项目中实现了对文本内容进行压缩（缩短）和扩展（延长）的功能，这可以视为上下文工程的一部分：

- src/prose/graph/prose_shorter_node.py ：实现了文本压缩功能，通过LLM将较长的文本内容缩短
- src/prose/graph/prose_longer_node.py ：实现了文本扩展功能，通过LLM将较短的文本内容扩展
这些功能可以用于消息历史的压缩和管理，但在代码中并没有明确将其用于消息历史压缩的证据。

#### 2. 消息状态管理
项目使用了 langgraph 库中的 MessagesState 作为基础状态类，用于管理消息历史：

- src/graph/types.py 中定义了继承自 MessagesState 的 State 类
- src/prose/graph/state.py 中定义了继承自 MessagesState 的 ProseState 类
- src/podcast/graph/state.py 中定义了继承自 MessagesState 的 PodcastState 类
这些类都继承了 MessagesState ，表明项目使用了 langgraph 库提供的消息历史管理功能。但是，在查看的代码中，没有发现对消息历史进行特殊处理（如总结、删除等）的明确实现。

#### 3. 增强的消息处理
在 src/llms/providers/dashscope.py 中，项目扩展了 ChatOpenAI 类，实现了 ChatDashscope 类，增加了对 reasoning_content 的支持：

- _convert_delta_to_message_chunk 函数处理消息块，包括提取 reasoning_content
- _convert_chunk_to_generation_chunk 函数将消息块转换为生成块
- ChatDashscope 类扩展了 ChatOpenAI ，支持处理 reasoning_content
这表明项目对消息内容进行了增强处理，但这主要是为了支持模型的推理过程，而非专门用于上下文窗口管理。