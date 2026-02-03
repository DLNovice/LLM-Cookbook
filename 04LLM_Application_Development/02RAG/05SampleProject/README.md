```
uv venv --python 3.12
source .venv/bin/activate
```



### 1、内容解析 parsing

#### 1）Mineru解析文档

借助Mineru将文档解析为Markdown，占用了26g显存

```bash
uv pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple
# uv pip install -U "mineru[all]" -i https://mirrors.aliyun.com/pypi/simple 
uv pip install -U "mineru[all]"

# 首次使用户级自动下载模型权重，其次<input_path>注意指向为具体的文件路径（docx没解析成功，转为pdf解析成功）
export MINERU_MODEL_SOURCE=modelscope
mineru -p <input_path> -o <output_path>
```

解析后的目录结构：输出Markdown效果还不错

```bash
$ CUDA_VISIBLE_DEVICES=1 mineru -p data/demo.pdf -o output
$ tree
.
├── data
│   ├── demo.docx
│   └── demo.pdf
├── output
│   └── demo
│       └── hybrid_auto
│           ├── demo_content_list.json
│           ├── demo_content_list_v2.json
│           ├── demo_layout.pdf
│           ├── demo.md
│           ├── demo_middle.json
│           ├── demo_model.json
│           ├── demo_origin.pdf
│           └── images
```



#### 2）后处理

但是发现，解析后的Markdown中，所有标题均为一级标题，不利于后续切分，Mineru似乎封装了解决方法，但据说效果暂时不佳，这里自己撰写一份简易代码进行解决：

```bash
# 环境配置：1、配置.env；2、安装python依赖
uv pip install -U langgraph -i https://pypi.tuna.tsinghua.edu.cn/simple
uv pip install -U langchain -i https://pypi.tuna.tsinghua.edu.cn/simple
uv pip install -U langchain-openai langchain-anthropic IPython
uv pip install python-dotenv
```

```python
import re
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(override=False)  # override=False 避免.env覆盖系统环境变量

# ========== 1. 初始化 LLM ==========
llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    temperature=0.5,
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("BASE_URL")
)

# ========== 2. Prompt 模板 ==========
prompt = PromptTemplate(
    input_variables=["titles"],
    template="""
你是一个技术文档编辑专家。

下面是一组 Markdown 标题，当前全部是一级标题（#），
请你根据标题语义与编号结构，判断它们应属于的层级，
并返回“重构后的 Markdown 标题”。

规则参考：
- “第X章” → #
- 章节名称（无编号） → ##
- X.Y → ###
- X.Y.Z → ####

仅返回重构后的标题列表，每行一个，不要添加解释。

标题如下：
{titles}
"""
)

# ========== 3. LCEL Chain ==========
chain = prompt | llm | StrOutputParser()

# ========== 4. 读取 Markdown ==========
input_path = Path("output/demo/hybrid_auto/demo.md")
output_path = Path("output/demo/hybrid_auto/demo_restructured.md")

text = input_path.read_text(encoding="utf-8")
lines = text.splitlines(keepends=True)

# ========== 5. 提取标题 ==========
raw_title_lines = [
    line.strip()
    for line in lines
    if line.lstrip().startswith("#")
]

# 去掉 # 符号
pure_titles = [
    re.sub(r"^#+\s*", "", title)
    for title in raw_title_lines
]

# ========== 6. 调用 LLM 重构层级 ==========
response = chain.invoke(
    {"titles": "\n".join(pure_titles)}
)

new_titles = [line.strip() for line in response.splitlines()]

# ========== 2. Prompt 模板==========
# =========================
# 7. 建立映射关系
# =========================
title_mapping = dict(zip(raw_title_lines, new_titles))

# ========== 8. 写回新 Markdown ==========
new_lines = []

for line in lines:
    stripped = line.strip()
    if stripped in title_mapping:
        new_lines.append(title_mapping[stripped] + "\n")
    else:
        new_lines.append(line)

output_path.write_text("".join(new_lines), encoding="utf-8")

print("✅ 标题重构完成，已生成:", output_path)

```

示例输入输出：

```python
# 第十四章
# 输配电及厂内外电源系统
# 14.1 主变压器和高压厂用变压器系统
# 14.1.1 系统功能
# 14.1.2 系统描述

# 第十四章
## 输配电及厂内外电源系统
### 14.1 主变压器和高压厂用变压器系统
#### 14.1.1 系统功能
#### 14.1.2 系统描述
```



### 2、切分 chunking

```bash
uv pip install langchain_text_splitters
```

示例代码：针对当前文档特殊性，需要仅按照三级标题进行切分，忽略一二级标题

```python
from typing import TypedDict, List

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from langgraph.graph import StateGraph, END
from pathlib import Path

# =====================================================
# 1. State 定义
# =====================================================

class MDState(TypedDict):
    raw_md: str
    section_docs: List[Document]


# =====================================================
# 2. Graph Nodes
# =====================================================

def load_markdown(state: MDState) -> MDState:
    return state


def split_by_h3(state: MDState) -> MDState:
    """
    ✅ 仅按三级标题（###）切分
    - ### 作为 chunk 起点
    - #### 自动归属到最近的 ###
    - # / ## 仅作为 metadata
    """

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "h1"),
            ("##", "h2"),
            ("###", "h3"),  # ⭐唯一切分边界
        ],
        strip_headers=False,
    )

    docs = splitter.split_text(state["raw_md"])

    # ✅ 只保留真正的三级章节
    docs = [doc for doc in docs if "h3" in doc.metadata]

    return {
        **state,
        "section_docs": docs,
    }


# =====================================================
# 3. 构建 LangGraph
# =====================================================

def build_graph():
    graph = StateGraph(MDState)

    graph.add_node("load", load_markdown)
    graph.add_node("split_h3", split_by_h3)

    graph.set_entry_point("load")

    graph.add_edge("load", "split_h3")
    graph.add_edge("split_h3", END)

    return graph.compile()

if __name__ == "__main__":
    input_path = Path("output/demo/hybrid_auto/demo_restructured.md")
    md_text = input_path.read_text(encoding="utf-8")

    app = build_graph()

    result = app.invoke({
        "raw_md": md_text
    })

    print("最终切分结果：\n")
    for i, doc in enumerate(result["section_docs"], 1):
        print(f"--- Chunk {i} ---")
        print(doc.page_content.strip())
        print("metadata:", doc.metadata)
        print()

```

由输出可知，切分效果良好，正确的将当前的8个三级标题及其内容，切分为了8个Chunk。



### 3、向量化 embedding

#### 1）数据库准备

数据库准备：这里基于docker部署[Milvus](https://milvus.io/docs/zh/install_standalone-docker.md)，在基于pymilvus对其连接使用

```bash
$ curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh

$ bash standalone_embed.sh start

$ docker ps
11703****** milvusdb/milvus:v2.6.8 "/tini -- milvus run…" 16 seconds ago  Up 14 seconds (healthy)  0.0.0.0:2379->2379/tcp, [::]:2379->2379/tcp, 0.0.0.0:9091->9091/tcp, [::]:9091->9091/tcp, 0.0.0.0:19530->19530/tcp, [::]:19530->19530/tcp milvus-standalone
```

连接测试：`uv pip install -U pymilvus`

```python
from pymilvus import MilvusClient

client = MilvusClient("http://localhost:19530")
```



#### 2）向量化

这里文档量不大，图省事，直接用Ollama下载了一个`qwen3-embedding:8b`使用。

```bash
uv pip install langchain_community
```

注意:

- 相比之前的切分代码，不能直接存入向量库，注意补齐metadata，且注意代码逻辑，不要只存入标题、没存内容
- collection 每次运行前清空，避免多次运行导致脏数据

```python
from pathlib import Path
import re

from pymilvus import connections, utility

from langchain_core.documents import Document
from langchain_community.vectorstores import Milvus
from langchain_community.embeddings import OllamaEmbeddings

from langgraph.graph import StateGraph, END
from langchain_text_splitters import MarkdownHeaderTextSplitter


# 1. Markdown 预处理：H4 降级
def demote_h4(markdown: str) -> str:
    return re.sub(r"^####\s+", "", markdown, flags=re.MULTILINE)


# 2. LangGraph State
class MDState(dict):
    raw_md: str
    section_docs: list[Document]


# 3. LangGraph Nodes
def load_markdown(state: MDState) -> MDState:
    return state


def split_by_h3(state: MDState) -> MDState:
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "h1"),
            ("##", "h2"),
            ("###", "h3"),
        ],
        strip_headers=False,
    )

    docs = splitter.split_text(state["raw_md"])
    docs = [doc for doc in docs if "h3" in doc.metadata]

    return {
        **state,
        "section_docs": docs,
    }


# 4. 构建 LangGraph
def build_graph():
    graph = StateGraph(MDState)

    graph.add_node("load", load_markdown)
    graph.add_node("split_h3", split_by_h3)

    graph.set_entry_point("load")
    graph.add_edge("load", "split_h3")
    graph.add_edge("split_h3", END)

    return graph.compile()


# 5. 主流程
if __name__ == "__main__":

    COLLECTION_NAME = "power_doc_rag"

    # 先连接 Milvus
    connections.connect(
        alias="default",
        host="localhost",
        port="19530"
    )

    # ---------- 开发阶段：启动即清空 ----------
    if utility.has_collection(COLLECTION_NAME):
        utility.drop_collection(COLLECTION_NAME)
        print(f"[INFO] Dropped existing collection: {COLLECTION_NAME}")

    # ---------- Embedding ----------
    embeddings = OllamaEmbeddings(
        model="qwen3-embedding:8b",
        base_url="http://localhost:11434"
    )

    # ---------- VectorStore ----------
    vectorstore = Milvus(
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
        connection_args={
            "host": "localhost",
            "port": "19530",
        },
        auto_id=True,
    )

    # ---------- 读取 Markdown ----------
    input_path = Path("output/demo/hybrid_auto/demo_restructured.md")
    raw_md = input_path.read_text(encoding="utf-8")

    # H4 降级（核心）
    raw_md = demote_h4(raw_md)

    # ---------- LangGraph 切分 ----------
    app = build_graph()
    result = app.invoke({"raw_md": raw_md})

    docs = result["section_docs"]

    # ---------- metadata 补齐 ----------
    for doc in docs:
        h1 = doc.metadata.get("h1", "")
        h2 = doc.metadata.get("h2", "")
        h3 = doc.metadata.get("h3", "")
        clause_no = h3.split()[0] if h3 else ""

        doc.metadata.update({
            "clause_no": clause_no,
            "section_path": " > ".join(x for x in (h1, h2, h3) if x),
            "source": input_path.name,
        })

    # ---------- 入库 ----------
    vectorstore.add_documents(docs)
    print(f"[INFO] Inserted {len(docs)} documents into Milvus")

    # ---------- 检索测试 ----------
    print("\n======= 检索测试 =======\n")
    results = vectorstore.similarity_search(
        "主变压器 系统功能",
        k=3
    )

    for i, r in enumerate(results, 1):
        print(f"\n===== Result {i} =====")
        print("clause_no:", r.metadata.get("clause_no"))
        print("h3:", r.metadata.get("h3"))
        print("section_path:", r.metadata.get("section_path"))
        print("\n--- 正文内容 ---")
        print(r.page_content)


```

示例结果：

```bash
======= 检索测试 =======

===== Result 1 =====
clause_no: 14.1
h3: 14.1 主变压器和高压厂用变压器系统
section_path: 第十四章 > 输配电及厂内外电源系统 > 14.1 主变压器和高压厂用变压器系统
--- 正文内容 ---
......

===== Result 2 =====
clause_no: 14.4
h3: 14.4 发电机变压器组保护系统
section_path: 第十四章 > 输配电及厂内外电源系统 > 14.4 发电机变压器组保护系统
--- 正文内容 ---
......
```



### 4、检索 retrieval 与 排序 reranking

```bash
uv pip install rank_bm25
uv pip install -U langchain-ollama langchain-milvus
```

示例代码：这里rerank模型暂时使用`qwen3:30b`

```python
from pymilvus import connections

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_community.retrievers import BM25Retriever

from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_milvus import Milvus

from typing import List
from pydantic import Field
from pydantic import ConfigDict


# 1. Milvus 连接
COLLECTION_NAME = "power_doc_rag"

connections.connect(
    alias="default",
    host="localhost",
    port="19530"
)

embeddings = OllamaEmbeddings(
    model="qwen3-embedding:8b",
    base_url="http://localhost:11434"
)

vectorstore = Milvus(
    embedding_function=embeddings,
    collection_name=COLLECTION_NAME,
    connection_args={
        "host": "localhost",
        "port": "19530",
    },
    auto_id=True,
)

# 2. Vector Retriever
vector_retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 6}
)

# 3. BM25 Retriever（工程简化方案）
all_docs = vectorstore.similarity_search(
    query="*",  # 只为取文档
    k=2000
)

bm25_retriever = BM25Retriever.from_documents(all_docs)
bm25_retriever.k = 6

# 4. Hybrid Retriever（LangChain 1.0 正确实现）
class HybridRetriever(BaseRetriever):
    bm25: BaseRetriever = Field(...)
    vector: BaseRetriever = Field(...)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager=None,
    ) -> List[Document]:
        docs_bm25 = self.bm25.invoke(query)
        docs_vector = self.vector.invoke(query)

        doc_map = {}
        for d in docs_bm25 + docs_vector:
            key = d.metadata.get("section_path", d.page_content[:80])
            doc_map[key] = d

        return list(doc_map.values())


hybrid_retriever = HybridRetriever(
    bm25=bm25_retriever,
    vector=vector_retriever
)

# 5. Reranker（LLM-based）
rerank_llm = OllamaLLM(
    model="qwen3:30b",
    base_url="http://localhost:11434",
    temperature=0
)


def rerank(query: str, docs: List[Document], top_n: int = 3) -> List[Document]:
    scored = []

    for doc in docs:
        prompt = f"""
你是一个技术文档检索评估器。

问题：
{query}

文档内容：
{doc.page_content}

请判断该文档对回答问题的相关性，给出 0~10 的分数。
只输出数字。
"""
        score_text = rerank_llm.invoke(prompt).strip()

        try:
            score = float(score_text)
        except Exception:
            score = 0.0

        scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:top_n]]


# 6. 执行完整 RAG 检索链路
if __name__ == "__main__":

    query = "主变压器 系统功能 是什么？"

    print("\n======= Hybrid Retriever =======\n")
    hybrid_docs = hybrid_retriever.invoke(query)

    for d in hybrid_docs:
        print(d.metadata.get("clause_no"), d.metadata.get("h3"))

    print("\n======= Rerank Top-3 =======\n")
    final_docs = rerank(query, hybrid_docs, top_n=3)

    for i, d in enumerate(final_docs, 1):
        print(f"\n--- Rank {i} ---")
        print("clause:", d.metadata.get("clause_no"))
        print("title:", d.metadata.get("h3"))
        print("path:", d.metadata.get("section_path"))
        print("\n正文片段：")
        print(d.page_content[:500])

```

示例结果：

```bash
======= Hybrid Retriever =======

14.4 14.4 发电机变压器组保护系统
14.2 14.2 发电机并网系统
......

======= Rerank Top-3 =======--- Rank 1 ---
clause: 14.4
title: 14.4 发电机变压器组保护系统
path: 第十四章 > 输配电及厂内外电源系统 > 14.4 发电机变压器组保护系统

正文片段：
......
```


