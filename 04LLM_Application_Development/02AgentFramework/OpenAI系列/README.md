## 时间线 & 关键节点

目前 2025.11 ，可知：

- 最初（2019–2022 年代）OpenAI 主要通过较基础的 “Completions API” 提供文本生成能力 —— 也就是让模型「继续／补完文本」
- 随着对话式模型（聊天／多轮对话）的兴起，OpenAI 推出了 **Chat Completions API** —— 通过指定 “system / user / assistant” 的角色，实现对话式交互。这个 API 成为构建聊天机器人／对话系统的标准方式
- 随着能力提升（模型变强、multimodal 能力、工具调用能力、复杂／多步任务能力变强），OpenAI 在 2023–2024 年期间尝试更“agent 化”（agentic）的方式 —— 例如允许模型调用工具、执行自动化任务等。为此引入了 **Assistants API（beta）** —— 这是迈向“AI 不只是回复，而是能主动做事／操作工具”的尝试
- 不过，Assistants API 虽然有很多潜力，但开发者反馈说“设计上不够优雅／灵活”——采用上有阻碍。于是 OpenAI 决定设计一个“兼顾易用 + 功能 + 拓展性”的统一方案。结果就是 **Responses API** —— 2025 年 3 月 11 日正式发布
- 同时，为了方便构建更复杂／多 agent 的系统，还推出了 **Agents SDK**，以及 “内置工具”（如 Web Search、File Search、Computer Use 等），方便 agent 调用实际工具、访问网络／文件／系统
- 根据官方文档，目前 Responses API 已被定位为「未来主流／推荐」API
- 据公开资料，Assistants API 的支持将在 **2026 年中期左右** 被废弃／下架
- 同时，虽然 Chat Completions API 会继续被保留用于简单对话用途，但从此以后，新的功能、新的特性基本都优先／仅在 Responses API 中出现。