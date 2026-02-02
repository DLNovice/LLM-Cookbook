## 评估指标

> 目前从实用效果来看，平时主要一方面看检索效果，另一方面就是大模型自行生成QA（人工检查一下A）然后自行评估生成质量，如果要上线的话，需要加入一些真实数据集人工评测一下效果

RAG 效果评估通常从以下几个维度展开：

| 维度               | 关注点                                | 常见指标                         |
| ------------------ | ------------------------------------- | -------------------------------- |
| **检索效果**       | 检索到的候选文档/片段是否高质量、相关 | Recall@K, MRR, Precision@K       |
| **生成质量**       | 生成文本的准确性、流畅性              | BLEU, ROUGE, METEOR, BERTScore   |
| **知识一致性**     | 生成内容与事实/检索内容是否一致       | Fact-based metrics, Faithfulness |
| ~~**任务实用性**~~ | ~~在具体任务中的表现~~                | ~~QA 准确率、F1、特定业务指标~~  |

备注：检索效果、生成质量大家提到的比较多，其他指标比较杂，目前没确定哪些是核心关注的指标。



### 检索效果

用途：评估检索模块是否高效提供支持生成的候选证据

- Recall@K（召回率）
   检索结果中覆盖真实相关文档/段落的比例（通常 K=5 / 10）。
- Precision@K（精确率）
   前 K 条结果中相关文档的比例。
- MRR (Mean Reciprocal Rank)
   第一个相关结果出现的位置倒数的均值。



### 生成质量

语言质量指标（通用文本生成指标）‍：传统 NLP 文本生成指标适用于衡量生成内容与参考文本的相似性，目前典型用于 QA、摘要、对话等生成任务对比测试

- BLEU / ROUGE / METEOR
   主要衡量 n-gram 重叠。
- BERTScore / BLEURT / COMET
   基于语义的相似度评估，较能捕捉意图一致性。



### 知识一致性/ 协同度指标（RAG Triad）

RAG 系统强调“回答不应该是无根据的发明（hallucination）”，因此需要专门评估 factuality，真实性 / 无胡乱生成指标如下：

| 指标                     | **描述**                               |
| ------------------------ | -------------------------------------- |
| Faithfulness Score       | 内容与支持证据之间的一致性             |
| Hallucination Rate       | 与检索/知识库矛盾的生成比例            |
| Entailment based metrics | 使用语言推理模型判断生成是否被证据蕴含 |

补充：

- Context Precision / Recall：检索到的上下文中，有多少信息被生成模型正确地利用了。
- Answer Relevancy：答案是否直接针对用户的问题，而不是偏离主题。
- Answer Correctness：答案本身是否正确，即使不考虑上下文也应是对的。

代表性指标/方法如下：

- RAGAS：一个专门针对 RAG 的评估框架，提供了如 Faithfulness（答案是否有依据）、Context Relevance（检索上下文是否相关）等指标。
- TruLens：流行的“RAG三元组”指标（Context Relevance, Groundedness, Answer Relevance），专注于检测幻觉。
- LLM-as-a-Judge：利用更强大的 LLM（如 GPT-4）对生成答案进行评估，判断其是否“基于证据”生成。



### 人工评价

自动指标往往无法完全反映真实质量，因此人工评价仍是主流：

| 维度         | 说明                      |
| ------------ | ------------------------- |
| Relevance    | 问答/生成是否贴合用户查询 |
| Correctness  | 内容是否正确              |
| Fluency      | 表达是否自然              |
| Faithfulness | 与证据的一致性            |
| Usefulness   | 是否对用户有帮助          |



## Others

参考：

- https://github.com/RwandanMtGorilla/Kumi