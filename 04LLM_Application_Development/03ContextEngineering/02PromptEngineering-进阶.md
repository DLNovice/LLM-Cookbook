## 进阶技巧

### Summery

> 以下总结不做实时更新（维护成本较高），仅作为参考清单，实际编写Prompt时，建议阅读全文。
>
> 参考来源包括：
>  1）主流模型/平台官方博客（Anthropic、OpenAI 等）
>  2）社区一线实践经验（阿里技术公众号、小红书等）
>  3）成熟产品中的真实 Prompt（如 Claude Code）

**1️⃣ 我想让模型“扮演谁 & 做什么”？ **Role / Objective / Instruction / Rules

- 角色（Role）
- 目标（Goal）
- 边界与规则（Constraints）

**2️⃣ 我是否需要模型“思考”？思考到什么程度？** CoT / Structured Reasoning / Planning / Reflection

- 是否需要 CoT
- 显式 vs 隐式思考
- 用结构引导，而不是一句“请认真思考”

**3️⃣ 输入怎么组织，模型才不迷路？ **Delimiters / XML Tags / Prompt Organization

- 分段
- 标签（XML / Markdown）
- 把“数据”和“指令”分离

**4️⃣ 我能不能用示例“画给它看”？** Few-shot / Examples / Pattern Induction

- Few-shot
- 不追求全覆盖，而是“范式对齐”
- 避免重复导致模式僵化

**5️⃣ 输出是不是“可控、可接系统”的？** Structured Output / Schema / Validation

- Schema
- JSON / 表格 / checklist
- 为下游系统服务



### Reference

学习各大产品的Prompt逆向工程：

- https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools
- [Google - Gemini 提示工程](https://github.com/elder-plinius/CL4R1T4S)

开源Prompt集合：

- [LangChain Hub](https://smith.langchain.com/hub)



各大厂商的Prompt设计原则：

Google:
- https://services.google.com/fh/files/misc/gemini-for-google-workspace-prompting-guide-101.pdf
- https://ai.google.dev/gemini-api/docs/prompting-strategies?hl=zh-cn

Anthropic:
- [Anthropic: Prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)，具体技巧如下：
  - **提示词生成器：**我们创建了一个提示生成工具，该工具引导Claude生成针对您特定任务的高质量提示模板。
  - **清晰、直接、详细：**三个方面，可以结合Claude官方示例辅助理解，1、给出语境信息（任务用于什么、输出面向什么手中、任务属于什么工作流的什么位置、任务的最终目标）；2、具体说明要Claude做什么；3、使用编号或项目符号，使指令有顺序。
  - **使用示例（多轮提示）：**提供有效的示例，注意1、相关（贴合实际用例）；2、多样（涵盖边缘情况和潜在挑战）；3、清晰（使用examples标签）
  - **让Claude思考：**首先确定什么时候需要思考什么时候不要思考；如何在Prompt中定义好如何思考？结合案例，理解如下三个核心，1、基础的CoT；2、通过结构引导CoT；3、结构化的Prompt
  - **使用XML标签：**（对Claude外的其他服务商，XML未必最佳，但是同样有用，OpenAI、Gemini都提到股XML标签）标签、标签嵌套
  - **角色定义：**参考官方案例即可
  - **预填充模型的回复：**预先添加一部分对话
  - **链式复杂提示：**何时使用？如何使用？（例如：内容创作管道：研究 → 概要 → 草稿 → 编辑 → 格式）
  - **长上下文提示：**1、将长篇数据置于顶部；2、使用XML标签结构化文档内容和元数据；3、对于长文档，执行任务前先引用文档相关部分（涉及动态Prompt）
  - **扩展思考提示：**（类似Qwen3打开推理模式）扩展思维是部分Claude模型的一个额外功能，通过向模型服务商发送请求时添加起一个参数，完成启用。

OpenAI:
- [2025.4.14：GPT-4.1 Prompting Guide](https://cookbook.openai.com/examples/gpt4-1_prompting_guide)，具体内容如下
  - **Agentic Workflows**：
    - 系统提示提醒（可copy官方示例）：注意三个关键类型的提醒，1、持久性；2、工具调用；3、规划（可选）
    - 工具调用：鼓励开发者仅使用工具字段来传递工具，而不是手动将工具描述注入到您的提示中并为工具调用编写单独的解析器
    - 规划 & 思维链：提示Agent在工具调用之间进行规划和反思
    - 案例：分享了一个提高了SWE-bench的得分的提示词案例
  - **Long context**：
    - Optimal Context Size
    - Tuning Context Reliance
    - Prompt Organization
  - **思维链**：非推理模型可以通过Prompt实现CoT
  - **指令遵循**：
    - 推荐工作流
    - 常见故障模式
    - 示例：客户服务
  - **一般建议**：提示结构、分隔符、注意事项

- [Prompt caching](https://platform.openai.com/docs/guides/prompt-caching) 通过提示缓存（模型提示通常包含重复内容），降低延迟和成本

  - **概述：**举例，如果你有一个 chatbot，每次对话你都会重复发送一段说明（例如系统提示 + 工具列表 + prompt 模板），这些内容没变；然后再加上用户的新问题。这种情况下，这段没变的部分就是 “可缓存的”，OpenAI 可以缓存它，后面请求里只处理“新”的部分。

  - **工作原理：**略

  - **缓存中有哪些数据：**消息、图片、工具使用、结构化输出

  - **实践：**略

  - **简化流程：**简单来说，Prompt Caching 是 OpenAI API 提供的一项机制

    ```
    请求发出 → 拆 token → 看前 1,024 token 的 prefix 是否已有缓存
        ├ 是 → Cache Hit → 重用那部分中间状态／计算 → 新部分继续处理 → 输出 → 折扣 + 较低延迟
        └ 否 → Cache Miss → 完整处理 prompt → 将前面（至少 1,024 token，之后每 128 个 token 增加） 的 prefix 存入缓存 → 输出
    缓存项如果 5-10 分钟无活动可能被清除；无论怎样，最长在一小时内会被移除或刷新。
    ```

    

参考：[一文掌握：AI Agent Prompt是什么？智能体Prompt如何设计？](https://mp.weixin.qq.com/s/A0BrFNBu0B0-XT1iiBkcHQ)

- 五个核心要素：角色定义、核心目标、行为规则、资源调用、容错机制
- 四步指南：明确Agent的核心场景、编写结构化的Prompt模板、声明资源或工具以及强化能力、测试及迭代增强
- 实用技巧-3个原则：越具体越精准、用 “规则清单” 替代 “抽象描述”、记得要预留“人工干预入口”



参考：[腾讯云 - 程序员必备！Prompt三大进阶技巧和实用模板](https://mp.weixin.qq.com/s/88XO2ooWkTuMJhhyQJ12MA)

- 基础技巧：角色定义、结构化输出、提供上下文
- 中级技巧：CoT、Few-Shot、约束条件设置、假设验证法、对比分析法、错误预演法
- 高级技巧：元提示（Meta-Prompting）、动态角色切换、渐进式优化、多维度评估、反向工程
- 实用模版：代码生成、问题诊断、技术调研



## 概念补充

#### 小Tips

写prompt时换行`\n`怎么用？一般不用主动打，直接回车即可

`\n`或者`\\n` 都可以，但是注意统一



#### 一些评估和优化Prompt的算法

参考：[大模型面试题：请说下常见的prompt优化方法](https://mp.weixin.qq.com/s/EpyT0gB098YL3eGijDcRhQ)

- 提到了优化Prompt相关的论文，如APE、ProTeGi、OPRO等



#### 关于不同上下文的优先级

常见有如下几种，当不同层次的提示发生冲突时，模型通常会遵循一个 **优先级层次**：

- System Prompt（系统提示）：定义规则，最高优先级
- Developer Prompt （如果存在，比如 API 里叫做 *assistant* 或 *developer*）：次之
- User Prompt（用户提示）：在不违反 system/dev 的情况下优先
-  Conversation Context（对话上下文）：主要用于连贯性，优先级最低。



模型本身不会“硬编码”什么是 system 或 user，它是依赖 **输入格式化** 来理解层级的。

-  比如 OpenAI 的 API 使用 **role-based messages**：

  ```
  [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "写一首诗"},
    {"role": "assistant", "content": "好的，以下是一首诗..."},
    {"role": "user", "content": "把它改成搞笑风格"}
  ]
  ```

- **role** 明确告诉模型消息的来源。

- 训练时模型就学会了：`system > developer > user > assistant` 的权重。



模型内部是怎么“理解”的？

- 模型并不是显式地执行逻辑，而是通过 **训练语料和标注** 学会了优先遵守 system 指令。
- 在 RLHF（人类反馈强化学习）阶段，训练数据会强化：
  - 遵守 system 提示 → 奖励高
  - 违背 system 提示 → 奖励低
- 因此模型在生成时 **自然地会把 system prompt 当作“最强约束”**。