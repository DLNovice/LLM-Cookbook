Github：https://github.com/huggingface/smolagents

官方文档：https://huggingface.co/docs/smolagents/index

大佬博客：[SmolAgents快速上手：最优雅的Agent构建工具](https://zhuanlan.zhihu.com/p/20291433412)



# 概述

**smolagents**是[HuggingFace](https://zhida.zhihu.com/search?content_id=253080549&content_type=Article&match_order=1&q=HuggingFace&zhida_source=entity)官方推出的Agent开发库，HF出品的库，往往的设计理念是“低门槛，高天花板，可拓展”。



特色：

- 极简设计：高度精简的架构设计，使开发者能够迅速理解和入门。Minimal 抽象（Minimal Abstraction）层意味着更容易自定义改造，也更适合快速原型开发。
- 行动即代码：将所有的操作写成代码，本质上，这是一个可以即时生成代码并执行的代理,如果遇到错误，还能自动恢复和重写。
- 模型与工具支持：
  - 模型无关（Model-agnostic）：可接入 Hugging Face Hub 上的 Transformers 模型，也支持通过 LiteLLM 使用 OpenAI、Anthropic 等云端模型，还可运行本地如 Ollama。
  - 工具无关（Tool-agnostic）：可调用来自 MCP 服务器、LangChain、甚至直接使用 Hub Space 作为工具。
  - 得益于 Hugging Face Hub 的深度整合，工具和 agent 可被轻松共享和复用。
- 执行支持：提供安全的代码执行方式，包括使用 E2B sandbox 或 Docker 容器隔离环境。
- 多模态支持：支持文本、图像、视频、音频等多种输入形式（Modality-agnostic）。



## 概念补充

关于在 **SmolAgents** 里说的 **“Minimal 抽象（Minimal Abstraction）”**，意思是：

它尽量减少在框架层面人为加的“封装”和“层级”，让开发者能够直接和最核心的东西打交道，而不是被复杂的抽象层挡住。

------

举个例子

在一些主流 Agent 框架里（比如 LangChain、AutoGen）：

- 你要先定义 **工具（Tool）类**、**链（Chain）**、**执行器（Executor）** 等对象。
- 然后 agent 的调用会被框架层的逻辑“翻译”为 JSON，再交给 LLM，再由框架解析 JSON 并执行工具。
- 开发者很难看清楚 **到底 LLM 在做什么**，以及中间是否有性能浪费。

而在 **SmolAgents** 里：

- **没有繁琐的层级**，agent 就是一个简单的类，工具就是一个 Python 函数。
- LLM 输出的结果直接就是 **可执行 Python 代码**（例如 `search_web("smolagents")`），框架只管安全执行。
- 开发者能立刻看见 agent 生成的代码，逻辑透明、可控。

------

用一句话总结

**Minimal 抽象 = 少包一层壳，让你直接看到“骨架”**。

- 优点：透明、灵活、容易改造，适合快速实验。
- 缺点：对新手来说可能没有“现成的高级模块”，需要自己写逻辑。



# 实操

TODO