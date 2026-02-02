> 参考：[万字长文｜大语言模型结构化输出（Structured Output）的技术原理和实现](https://mp.weixin.qq.com/s/bT5Z9HBgLl2I4Ylbxklw0A)

本报告将沿着结构化输出技术从“软”到“硬”的演进路线，深入探讨六大核心技术路径：

- 模式引导生成（Prompt-Guided Generation）： 最基础的方法，通过精心设计的提示词进行软性引导。
- 验证与修复框架（Validation and Repair Framework）： 在生成后进行“事后”保障，确保输出合规。
- 约束解码（Constrained Decoding）： 从根本上限制模型生成过程，进行“事前”的硬性约束。
- 监督式微调（Supervised Fine-Tuning, SFT）： 通过数据集训练，使模型内化结构化输出的规则。
- 强化学习优化（Reinforcement Learning Optimization）： 采用奖励机制，突破SFT的性能瓶颈。
- 接口化能力（API Capabilities）： 将复杂技术抽象为简单易用的API功能。



仅供参考：

- **提示词工程：**
  - “必须输出JSON格式”、“严格遵守schema要求”、few-shot等
  - 提供开头和结尾的锚点
    - 预填充响应（Prefilling）： 让模型的响应以 `{"` 或 `[` 字符开始，可以有效引导模型进入 JSON 生成模式。
    - 使用自定义标签**：** 要求模型将 JSON 输出包裹在特定的标签内，如 `<JSON_OUTPUT>` 和 `</JSON_OUTPUT>`。这样即使模型输出了额外的无关文字，你也可以通过编程方式轻松地提取标签内的纯 JSON 内容。
- **JSON Mode / Schema 约束：**
  - 许多现代大模型的 API 都提供了专门的参数
  - 再比如SGLang（Structured Generation Language），其也具备让大语言模型（LLM）在推理时，强制遵循特定的结构化输出格式
- **后期处理和错误处理：**
  - 接收到模型输出后，立即尝试使用 `JSON.parse()` 或等效方法进行解析等等
- **约束解码结束：**
  - 该技术通过在生成过程中对每个token进行实时约束，确保输出严格符合JSON语法。常用工具包括Outlines和Guidance
