常见模型：

- BERT系列
- GPT系列
- LLama系列
- Qwen系列
- Deepseek系列
- Kimi系列



## 时间线

TODO



## Bert 系列

概述：

- **BERT模型**：是替代 Word2Vec 的预训练模型，通过 MLM 和 NSP 任务学习表征。 输入编码向量是 Position、Token 和 Segment Embedding 的单位和。 存在模型庞大、预训练和微调不匹配、收敛慢等缺点。
- **BART模型**：采用 encoder - decoder 架构，对标准 Transformer 模型做了改变。 更适合文本生成场景，也能用于文本理解任务。
- **T5模型**：是预训练语言模型领域的通用模型，将自然语言问题转化为文本到文本形式。 对于下游任务微调训练友好。
- **RoBERTa模型**：在模型规模、算力、数据和训练方法上对 BERT 进行改进。 去掉 NSP 任务，采用动态掩码和更大的 byte 级别 BPE 词汇表。
- **DeBERTa模型**：使用注意力解耦机制和增强的 mask 解码器改进了 BERT 和 RoBERTa。 引入虚拟对抗训练提高泛化能力。
- **MLM任务**：输入序列中 15% 的单词被 [MASK] 替换。 其中 80% 换为 [MASK]、10% 换为随机词、10% 保持不变，让模型基于上下文预测原单词。
- **NSP任务**：训练时模型接收成对句子，预测第二句是否为第一句后续。 50% 输入对是前后关系，50% 随机组成。



## GPT 系列

关键要点概述：包括论文、模型结构、训练范式等内容

- GPT1（2018）：
  - 论文：《Improving Language Understanding by Generative Pre-Training》
  - 模型结构：模型采用 12 层 Transformer decoder-only 结构，位置编码可训练，只用 mask multi-head attention
    - 采用 Decoder-only Transformer 架构，包含 12 层自注意力模块，隐藏维度 768，12 个注意力头，参数量约 1.17 亿。
    - 使用单向（causal）自注意力，仅利用历史上下文预测下一个词。

  - 训练范式：分为两阶段，即自监督预训练 + 有监督 fine-tune，预训练根据前 K 个词预测下一词，微调目标函数结合有监督和无监督目标函数；改变输入形式可实现不同下游任务
    - 无监督预训练：在 BooksCorpus 上训练标准语言模型（next-token prediction）。
    - 有监督微调：针对每个下游任务添加任务相关输出层，并在标注数据上微调整个模型。

  - 核心贡献：证明了生成式预训练语言模型可以作为通用表示，大幅提升多种 NLP 理解任务的性能，但仍依赖任务特定微调。

- GPT2（2019）：
  - 论文：《Language Models are Unsupervised Multitask Learners》
  - 模型结构：与 GPT1 基本一致，**post-norm 改为 pre-norm**，输入序列从 512 改为 1024，有 48 层
  - 训练范式：**预训练 + zero-shot**，核心思想是有监督任务是语言模型子集，大模型和丰富数据可完成有监督任务
  - 实验数据：来自 Reddit，共 800 万个文档、40GB；与 GPT1 相比
  - **核心贡献**：证明了“任务可以被视为语言的一部分”，语言模型本身即可在无示例情况下完成多种 NLP 任务。

- GPT3（2020）：
  - 论文：《Language Models are Few-Shot Learners》
  - 模型结构：在 GPT2 基础上应用 **Sparse attention**，可减少计算复杂度、处理更长输入序列
  - 训练范式：**预训练 + few-shot / in-context learning**；
  - **数据与能力**：使用混合的大规模语料（Common Crawl、Books、Wikipedia 等）。模型在多项任务中，仅凭少量上下文示例即可接近甚至超过微调模型性能。GPT3 数据量达 45T（清洗后 570G），最大模型参数为 1750 亿。
  - **核心贡献**：提出并验证了 **“Language Models are Few-Shot Learners”**，奠定了 **in-context learning** 与 Prompt Learning 作为新范式的基础。


| 维度       | GPT-1         | GPT-2                | GPT-3                    |
| ---------- | ------------- | -------------------- | ------------------------ |
| 参数规模   | 小            | 中                   | 极大                     |
| 训练范式   | 预训练 + 微调 | 纯预训练 + zero-shot | 纯预训练 + zero/few-shot |
| 任务适配   | fine-tuning   | prompt               | prompt                   |
| 核心突破   | 预训练有效    | zero-shot 可行       | few-shot 成立            |
| 模型统一性 | NLP 多任务    | 更强泛化             | 通用任务接口             |

------

在 **GPT-2** 的语境中，**zero-shot（零样本）** ：

- 概念：模型在没有看到任何该任务的示例、也没有针对该任务进行专门训练或微调的情况下，直接完成任务的能力。
- 例子：没有答案的情感分类/翻译/问答
- 为什么 GPT-2 能做到 zero-shot？1、超大规模预训练；2、任务被“语言化”了；3、不需要任务专用结构



## Qwen 系列

概述：

- **Qwen1模型特点**：基于Transformer改进，类似LLaMA结构，词汇表约152K，采用RoPE等技术；训练用自回归目标，用Flash Attention等加速；通过多种技术扩展上下文长度至推理时8192，奖励模型经预训练和微调。
- **Qwen1.5模型特点**：有Tokenizer BPE等“黄金四件套”，用Flash Attention；部分模型用GQA；Qwen1.5 - MoE - A2.7B有细粒度专家等；训练数据量未公布，支持32K上下文。
- **Qwen2模型特点**：与Qwen区别在GQA、YaRN + 双块注意力；预训练在质量、数据量和分布上改进；后训练有多种数据合成方法；RLHF分离线和在线两阶段。
- **Qwen2.5模型特点**：有多种参数量模型；结构与Qwen2一致；预训练数据18T tokens，有精细过滤等；长文本预训练分两阶段；后训练涵盖多方面能力提升。
- **Qwen3模型特点**：Attention模块有变化，如引入Query和Key的RMS Normalization等；预训练数据从18T tokens扩展到36T tokens，分三阶段训练；后训练采用四阶段流程。



## Llama系列

TODO
