本章主要包含PromptEngineer、ContextEngineer，以及Mem0等上下文工程相关框架。



## 待归纳

### 1、关于 MAS & Context Engineering

> 面对 Multi-Agent-System、Context Engineering、Agent Memory、RAG等方向层出不穷的新技术和博客，该如何结合具体场景去"取舍/使用"这些技术？

相关概述：

- [2025.06.13 Anthropic | How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)：架构模式 - 采用 Orchestrator-Worker（策划者-执行者） 模式。主智能体负责规划，并启动多个子智能体并行搜索和分析信息；关键结论 - 多智能体系统的优势在于并行化（Parallelization）和增加 Token 消耗以换取性能（研究发现 Token 消耗量与性能成正比）。
- [2025.06.12 Cognition (Devin 团队) | Don’t Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents#principles-of-context-engineering)：针对当前 MAS 的流行，笔者认为 MAS 往往是脆弱的。并提出了两大核心原则（共享上下文、决策隐喻）以及建议方案（优先使用单线程线性智能体；如果上下文过长，应通过“压缩（Compression）”而非拆分智能体来解决。）
- [2025.06.12 Cognition (Devin 团队) | How and when to build multi-agent systems](https://www.blog.langchain.com/how-and-when-to-build-multi-agent-systems/)：文章对比了上述 Anthropic 和 Cognition 的观点；提出了两个核心发现（“读”比“写”更容易并行、读写分离）
- [2025.07.02 Multi-Agent or Not, That Is the Question](https://medium.com/superagentic-ai/multi-agent-or-not-that-is-the-question-e80890459e12)：多智能体不是魔术，只有任务复杂到单线程无法处理时才应使用
- [2025.7.18 Manus | 构建 Manus 的上下文工程经验](https://manus.im/zh-cn/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)：他们放弃了微调（Fine-tuning），全力押注上下文工程（Context Engineering）。并提出了五大教训（KV 缓存设计、Masking 而非移除、文件系统即上下文、复述操控注意力、保留错误）
- [2025.09.29 Anthropic| Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)：开发重点已从单纯写好 Prompt 转向如何动态筛选和管理输入模型的信息流。介绍了“压缩、结构化笔记、子智能体架构”三大策略
- [2025.10.09 Agno (原 Phidata)| Context Engineering in Multi-Agent Systems](https://www.agno.com/blog/context-engineering-in-multi-agent-systems)：提供了非常具体的工程实现指导（系统提示词优化、上下文缓存、少样本学习、团队领导模式）
- [2026.01| Shichun-Liu/Agent-Memory-Paper-List](https://github.com/Shichun-Liu/Agent-Memory-Paper-List)：我们将代理记忆与 RAG 和上下文工程等相关概念区分开来，并通过三个统一的视角提供全面概述，形式（记忆载体是什么？）、功能（代理为何需要记忆？）、动态（记忆如何演变？）
- 等等（许多纯方法论的帖子不放在此处了，可参考其他章节内容）

**总结：**在搭建系统时，可以遵循以下路径

- **首选方案：单线程线性 Agent + 极致的上下文工程**（这里上下文工程和记忆系统不做详细区分，只谈方案）
  - 短期记忆 / 一般方法：滑动窗口、总结压缩、文件系统等等，Anthropic、Manus、Cursor、LangChain、Devin、阿里云等主流产品均有经验贴
  - 长期记忆存储：在任务结束后，让 Agent 自动进行“复盘”，将经验转化为长期记忆存入 RAG
- **性能瓶颈时：引入 MAS**（引入 MAS 不代表忽略 Context Engineering，恰恰相反，这是难点）
  - 只有当单线程 Agent 的上下文因信息量巨大而导致“注意力涣散”，或者任务需要物理意义上的并行（Parallelization）（如同时搜索 10 个网页）时，才引入 MAS
  - 可采用 Anthropic 推崇的引入 Orchestrator-Worker 并行处理“读”任务，其核心在于读写分离，读取信息可以高度并行，但最终决策（写入状态）应尽可能保持线性，以维持逻辑的一致性



### 2、Others

> 参考：[面试官问：Agent 的记忆模块是怎么实现的？](https://mp.weixin.qq.com/s/VTUBnBdpvRnMOhQ9tN6W5Q)

一、非常简略但是直观的文章，**从工程角度看，Agent 的记忆主要分为两类：**

- 短期记忆（Short-term / Context Memory）
- 长期记忆（Long-term / Persistent Memory）

二、**短期记忆：上下文缓存**

- 实现方式：通常就是将最近的 Prompt、Response 压缩成结构化的上下文缓存， 下一轮输入时，再把这些内容拼接进模型上下文
- 常见做法：Sliding Window（滑动窗口）、Summarization（摘要式记忆）、State Tracking（状态缓存）

三、**长期记忆：持久存储 + 向量检索**

| 结构             | 属于     | 功能                     | 问题域           | 类比                    |
| ---------------- | -------- | ------------------------ | ---------------- | ----------------------- |
| **向量数据库**   | 记忆存储 | 存 embedding，语义检索   | 如何存？如何找？ | 大脑的“海马体 + 图书馆” |
| **检索回顾机制** | 记忆调用 | 决策前检索并思考         | 如何用？         | 读过去的日记并反思      |
| **重要性筛选**   | 记忆写入 | 决定哪些内容值得长期存储 | 记什么？         | 选择性记忆机制          |

- 典型结构包括：
  1. **向量数据库（Vector Store）**
     - 把对话或文档内容转成 embedding 向量；
     - 存入 Milvus、Faiss、Weaviate、Chroma 等；
     - 当需要回忆时，通过语义相似度检索相关内容。
  2. **检索回顾（Retrieval + Reflection）机制**
     - 模型每次决策前，先从记忆库里查找相关内容；
     - 将检索结果拼回 prompt ；
     - 再由 LLM 决定如何利用这些信息。
  3. **重要性筛选（Memory Filtering）**
     - 不是什么都存，而是存“有意义”的片段；
     - 例如通过打分机制筛选出“影响后续决策”的记忆。
- 常见策略：短期用 Context 记当前，长期用 Vector Store 记历史

四、**Memory 模块在框架中的位置**

- 典型流程：

  ```
  Input → Retrieve Memory → Combine Context → LLM Reasoning → Output → Update Memory
  ```

- LangChain中Memory 接口：

  ```
  ConversationBufferMemory
  ConversationSummaryMemory
  VectorStoreRetrieverMemory
  ```

  

> 参考：[LightMem用3招重新设计了LLM的记忆](https://mp.weixin.qq.com/s/OkhdTQYmdqo_r7iub94rJg)

官方地址：

- https://arxiv.org/html/2510.18866
- https://github.com/zjunlp/LightMem

我们推出了一种名为LightMem的新存储系统，它在存储系统的性能和效率之间取得了平衡，核心如下：

| 模块       | 昵称     | 关键设计                       | 效果                       |
| :--------- | :------- | :----------------------------- | :------------------------- |
| **Light1** | 感觉记忆 | 预压缩 + 主题分段              | **砍掉 20-80% 冗余 Token** |
| **Light2** | 短期记忆 | 主题缓冲 + 到达阈值再摘要      | **API 调用 ↓ 17-177×**     |
| **Light3** | 长期记忆 | 在线“软更新”+ 睡眠离线并行合并 | **运行时 ↓ 1.7-12×**       |
