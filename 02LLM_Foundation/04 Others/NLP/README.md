### 发展历程

NLP 的发展，本质是从 **符号规则** → **统计建模** → **分布式语义表示** → **序列建模** → **全局注意力建模** → **大规模预训练语言模型**，不断增强模型对**上下文、语义和长距离依赖**的建模能力。

```
规则 → 统计 → 词向量
      ↓
   序列建模（RNN）
      ↓
  长依赖（LSTM）
      ↓
   注意力（Attention）
      ↓
 并行 & 全局（Transformer）
      ↓
 大规模预训练（BERT / GPT）
```

早期阶段：规则 & 统计 NLP（1980s–2000s）

- 规则系统（Rule-based NLP）：人工编写语法规则、词典，如 正则、CFG（上下文无关文法）
- 统计 NLP（Statistical NLP）：用概率统计语言规律，如 N-gram、HMM（隐马尔可夫模型）、CRF（条件随机场）

神经网络时代的开端：Word Embedding（2013）

- Word2Vec / GloVe 语义表示革命：关键突破在于，把词映射到连续向量空间（Embedding），词的“语义相似性”可以被计算

序列建模时代：RNN 系列（2014–2017）

- RNN：第一次真正“读句子”
- LSTM / GRU：解决长期依赖问题
- Seq2Seq + Attention：关键过渡

Transformer：范式级变革（2017）

- Transformer（2017）：彻底抛弃 RNN，用 Attention 建模一切

预训练语言模型时代：BERT & GPT（2018–至今）

- BERT：双向语义理解
- GPT 系列：生成式范式



### 方向概述

概述：NLP（自然语言处理）的**主要研究方向 / 任务**可以从「**理解**」「**生成**」「**结构化**」「**交互与应用**」几个层面来系统化理解。

| 类别 | 关键任务         |
| ---- | ---------------- |
| 理解 | 分类、NER、匹配  |
| 抽取 | 实体、关系、事件 |
| 生成 | 摘要、翻译、对话 |
| 检索 | 搜索、问答       |
| 工程 | RAG、向量库      |
| 前沿 | 多模态、大模型   |

#### 一、文本理解类（Natural Language Understanding, NLU）

1️⃣ 文本分类（Text Classification）

**任务**

- 情感分析
- 主题分类
- 意图识别
- 垃圾信息识别

**典型场景**

- 电商评论好评 / 差评
- 客服对话中的用户意图判断
- 舆情监控
- 垃圾邮件 / 评论审核

**模型与方案**

- 传统：TF-IDF + SVM / LR

- 深度学习：CNN / BiLSTM + Attention

- 预训练模型（主流）：

  - **BERT / RoBERTa / ERNIE**
  - 中文：MacBERT、Chinese-BERT

- 工业方案：

  > BERT + 全连接分类头，微调（Fine-tuning）

------

2️⃣ 序列标注（Sequence Labeling）

**任务**

- 命名实体识别（NER）
- 词性标注（POS）
- 分词（中文）

**典型场景**

- 医疗实体抽取（疾病、药品）
- 金融信息抽取（公司名、金额）
- 搜索引擎关键词理解

**模型与方案**

- 传统：CRF、HMM
- 深度学习：
  - BiLSTM-CRF
- 预训练模型：
  - **BERT + CRF**
  - RoBERTa + Span-based NER
- 工业强化：
  - 多任务学习（NER + 分类）

------

3️⃣ 句子语义匹配 / 相似度计算

**任务**

- 语义相似度
- 语义等价判断
- 重复问题检测

**典型场景**

- FAQ 问答匹配
- 搜索排序
- 法律 / 合同相似条款检测

**模型与方案**

- Siamese Network
- Sentence-BERT（**SBERT**）
- ColBERT（检索增强）
- 向量数据库（FAISS / Milvus）

**工程方案**

> SBERT → 向量化 → 向量检索 → 重排

------

#### 二、信息抽取（Information Extraction）

4️⃣ 关系抽取（Relation Extraction）

**任务**

- 实体之间关系识别

**典型场景**

- 知识图谱构建
- 金融风控（企业关系）
- 医疗知识库

**模型与方案**

- Pipeline：NER → RE
- 联合模型：
  - CasRel
  - GPLinker
- 预训练：
  - BERT + 多头分类

------

5️⃣ 事件抽取（Event Extraction）

**任务**

- 事件触发词
- 事件角色识别

**典型场景**

- 新闻分析
- 舆情监控
- 金融公告解析

**模型**

- BERT + Span
- OneIE
- UIE（**百度统一信息抽取**）

------

#### 三、文本生成类（Natural Language Generation, NLG）

6️⃣ 文本摘要（Summarization）

**任务**

- 抽取式摘要
- 生成式摘要

**典型场景**

- 新闻摘要
- 会议纪要
- 法律文书摘要

**模型**

- 抽取式：TextRank
- 生成式：
  - **BART / T5**
  - PEGASUS
  - ChatGPT / GPT-4

------

7️⃣ 机器翻译（Machine Translation）

**任务**

- 多语言翻译

**典型场景**

- 跨境电商
- 国际会议
- 内容本地化

**模型**

- Transformer（核心）
- MarianMT
- mBART
- NLLB

------

8️⃣ 文本生成 / 对话系统

**任务**

- 问答系统
- 聊天机器人
- 写作辅助

**典型场景**

- 智能客服
- AI 助手
- 教育陪练

**模型**

- GPT 系列（GPT-3 / 4）
- LLaMA / Qwen / Baichuan
- RAG（检索增强生成）

**工程方案**

> LLM + 向量检索 + Prompt Engineering + 工具调用

------

#### 四、搜索与推荐相关 NLP

9️⃣ 信息检索（Information Retrieval）

**任务**

- Query 理解
- 文档召回
- 相关性排序

**典型场景**

- 搜索引擎
- 企业知识库
- 法律 / 医疗检索

**模型**

- BM25（传统）
- DPR（Dense Passage Retrieval）
- ColBERT
- Hybrid Search（稀疏 + 稠密）

------

🔟 问答系统（Question Answering）

**任务**

- 抽取式 QA
- 生成式 QA

**场景**

- 知识库问答
- 企业内部问答

**模型**

- BERT-QA
- T5 / GPT
- RAG-QA

------

#### 五、多模态 & 前沿方向（扩展）

1️⃣1️⃣ 多模态 NLP

- 文本 + 图像 / 表格
- 模型：BLIP、LLaVA、GPT-4V

1️⃣2️⃣ 低资源 / 小样本学习

- Prompt Learning
- LoRA / Adapter
- In-context Learning

1️⃣3️⃣ 可信 NLP

- 可解释性
- 对抗样本
- 偏见检测



### 部分工具

Weights & Biases ≠ 可视化工具，它是一个 ML 实验管理平台（Experiment Tracking Platform）

- TensorBoard 只能“看”，但不能“管”实验
- W&B / MLflow = 实验的“数据库 + 控制台”

你跑了 200 个实验：三周后你问自己，“那个效果最好的实验是怎么跑的？”

- 不同 lr / batch size
- 不同 tokenizer
- 不同 prompt
- 不同 LoRA rank

Weights & Biases 解决四个核心问题：

| 问题         | W&B 的答案 |
| ------------ | ---------- |
| 实验参数太多 | 自动记录   |
| 实验结果分散 | 集中存储   |
| 实验不可复现 | 版本化     |
| 团队无法协作 | 云端共享   |

W&B 在大模型 / NLP 训练中的典型用法

- 场景 1：SFT / Instruction Tuning
  - 对比 prompt 模板
  - 对比数据清洗策略
  - 对比 LoRA 参数
- 场景 2：LoRA / Adapter 训练
  - rank / alpha 消融
  - base model 对比
  - freezing 策略对比
- 场景 3：RLHF / DPO
  - reward 曲线
  - KL penalty
  - 人类偏好样本分析

------

文本数据增强方法

- 词级（Lexical-level）增强
- 句法级（Syntactic-level）增强
- 语义级（Semantic-level）增强（主流）
- 模板驱动增强（Controlled Augmentation）
- 标签保持型增强（Label-preserving）
- 对抗式增强（Robustness-oriented）

不同任务的推荐增强策略：

- 文本分类 / 意图识别
  - 词级增强（EDA）
  - 回译
  - LLM 轻量重写
- NER / 序列标注
  - 实体替换
  - Span 级重写
  - 避免自由生成
- QA / 阅读理解
  - 问题重写
  - 同义问题生成
  - 负样本构造
- 指令微调（SFT）
  - LLM 重写（主）
  - Self-Instruct
  - Prompt 多样化
- RLHF / 偏好学习
  - 输出扰动
  - 对比样本构造

------

LabelStudio：支持文本图片等，参考：https://developer.aliyun.com/article/1173783

Prodigy：略，支持自动标注