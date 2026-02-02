概述：

- 01BasicKnowledge：RAG全链路基础知识
- 02VectorLibrary：Milvus、Faiss等向量库基础知识
- 03Framework：LangChain、LlamaIndex、GraphRAG等框架基础知识
- 04Architecture：一些RAG架构分享
- 05Others：其他知识



## 待归纳

### RAPTOR

简单来说，**RAPTOR**（Recursive Abstractive Processing for Tree-organized Retrieval）是一种专门针对**长文本**或**全文本**理解的增强检索技术。

传统的 RAG（检索增强生成）通常只能检索到一两个零散的文本切片，这让你在问“这本书的主旨是什么？”这种宏观问题时，AI 往往会“断章取义”。而 RAPTOR 就像是给 AI 装了一个**多级缩放的望远镜**。

------

一、核心原理

RAPTOR 的核心在于构建一棵**树状的索引结构**：

- **底层（叶子节点）：** 原始的文档切片（Chunks）。
- **聚类与概括：** 系统将语义相近的切片通过算法（如 GMM 聚类）聚在一起。
- **递归汇总：** 对每个聚类生成的摘要（Summaries）再次进行聚类和概括，直到生成一个覆盖全篇的最高层摘要。

二、为什么它比普通 RAG 强？

| **特性**       | **传统 RAG**                    | **RAPTOR**                                 |
| -------------- | ------------------------------- | ------------------------------------------ |
| **检索粒度**   | 仅限局部切片                    | **跨层级**（从细节到全局摘要）             |
| **擅长问题**   | “XX 的电话是多少？”（事实检索） | “这篇文章的核心观点演变过程？”（总结检索） |
| **上下文理解** | 容易丢失长程关联                | 通过摘要链保留了全局语境                   |

三、工作流程

1. **构建树：** 递归聚类并生成摘要，形成从局部到整体的树状结构。
2. **多层检索：** 当用户提问时，同时在所有层级（原始切片 + 各级摘要）中寻找最相关的向量。
3. **综合生成：** 将不同层级的上下文提供给 LLM，让其既能看到细节，又能把握大局。

------

> **一句话总结：**
>
> RAPTOR 通过**递归摘要**构建了一棵“知识树”，让 AI 既能看到森林（大局观），也能看清树木（细节）。

RAPTOR 的实现流程可以分为：**聚类 -> 摘要 -> 递归构建 -> 扁平化检索**。下面是使用 LangChain 的组件来构建 RAPTOR 索引的示例代码：

```python
from langchain_experimental.raking_paths.raptor import RecursiveRetriever
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma

# 1. 初始化模型
model = ChatOpenAI(model="gpt-4-turbo")
embeddings = OpenAIEmbeddings()

# 2. 定义 RAPTOR 处理器
# 注意：这是 LangChain 实验性封装的逻辑简化版
# 它会自动执行：聚类 -> 生成摘要 -> 递归直到无法再聚类
raptor_retriever = RecursiveRetriever(
    documents=docs,               # 你的原始文档列表
    model=model,                  # 用于生成摘要的 LLM
    embeddings=embeddings,       # 用于聚类的向量模型
    max_clusters=10,              # 每层最大聚类数
    vectorstore_cls=Chroma        # 最终存储索引的向量库
)

# 3. 集成到 QA 链中
from langchain.chains import RetrievalQA

qa_chain = RetrievalQA.from_chain_type(
    llm=model,
    retriever=raptor_retriever.as_retriever()
)

# 4. 提问
response = qa_chain.run("分析整本书中主角性格的变化趋势")
```