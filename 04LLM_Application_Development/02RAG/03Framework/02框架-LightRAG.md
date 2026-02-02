官网：https://github.com/HKUDS/LightRAG

## 概念

### 1、论文解读

#### 传统方案弊端

lightrag提出了传统RAG方案中存在的一些问题：

（1）常规的“chunk”数据块提取方式，较难识别和提取出各种实体对象之间的复杂联系；

（2）传统方案通常无法提供上下文背景，无法保持各种实体及相互之间联系的连贯性（使得信息处于一种“割裂”状态），造成无法有效回应实际用户请求。

或者说：

● 扁平的数据表示：许多方法依赖于扁平的数据表示，无法理解和检索实体之间复杂关系中的信息。这导致在回答涉及多个相互关联实体的复杂问题时，答案支离破碎，缺乏连贯性。

● 上下文感知不足：现有系统缺乏足够的上下文感知能力，难以在各个实体及其相互关系之间保持一致性，导致答案无法完全解答用户的查询。


#### 解决方案概述

lightrag方案提出了基于knowledge graph（kg）知识图谱的rag方案，[主要优化解决三个方面问题](https://zhuanlan.zhihu.com/p/13308637187)：

**（1）复杂数据信息的提取。确保能够从文档中提取出实体及关系的完整上下文联系。**

（参考2.1内容）构建了包含kg、及vector store，Json value store等多个数据库/文件，在node、edge、chunk之间建立了多重联系，包含了kg构建过程中提取的全部重要字段、以及原始的text chunk，并且支持vector和graph搜索，为后续query阶段环节建立了基础。

**（2）提升数据提取效率。主要针对kg知识图谱rag方案，提升效率，缩短响应时延。**

（参考2.2内容）设计了一种轻量级kg rag query机制，通过keyword方式，可分别对应到query阶段local、global等模式，简化了流程，实现了快速响应。

**（3）快速适应新增数据。能够针对新增数据构建kg知识图谱，方便与原kg进行整合。**

lightrag中内建了一种机制，可针对增量数据，在原kg中进行检索、合并等操作；后续还增加了Insert Custom KG操作，后续有机会再介绍。



参考：https://blog.csdn.net/qq_41185868/article/details/143607681

![image-20250915114635344](./assets/image-20250915114635344.png)



[双层检索机制](https://www.cnblogs.com/ggyt/p/18599536)：

![image-20250915115219507](./assets/image-20250915115219507.png)



[架构图](https://www.cnblogs.com/mengrennwpu/p/18515750)：文中还涵盖了对论文各个模块，以及LightRAG框架的核心机制（基于图的文本索引 + 双层索引机制 + 检索增强回答生成）的解读

![image-20250915114800003](./assets/image-20250915114800003.png)



### 2、一些推文

Google上暂时没找到比较好的文章，解读LightRAG项目。

一些推文：

- [优化 GraphRAG：LightRAG的三大改进](https://mp.weixin.qq.com/s/j_VZSLVZXcQvjUUuopTlew)
  - 🦋 1. 索引的构建：基于图的文本索引
  - 🦉 2. 检索逻辑的升级：双层级检索
  - 🐘 3. 更新机制的简化：增量更新



LightRAG与GraphRAG的区别与联系：

- [GraphRAG](https://github.com/microsoft/graphrag)：由微软24年4月推出
- [LightRAG](https://github.com/HKUDS/LightRAG)：由港大和北邮推出

快速总结：

1. LightRAG 的知识图谱可以增量更新。为了将新数据合并到现有的图形索引中，GraphRAG 还需要为以前的数据重建整个 KG
2. 结合了 graph indexing 和 standard embedding 方法构建知识图谱。相对于 GraphRAG 以社区遍历的方法，LightRAG 专注于实体和关系的检索，进而减少检索开销
3. Hybrid Query双层检索策略，结合了 local 和 global 方法检索
4. 推理速度更快。在检索阶段，LightRAG 需要少于 100 个token和一个 API 调用，而 GraphRAG 需要 社区数量 x 每个社区的平均令牌数量token

如何选择：LightRAG在复杂推理任务上不如GraphRAG全面

- 如果需要快速、简单的语义搜索，选LightRAG
- 如果涉及复杂逻辑或多文档关联分析，选GraphRAG（需权衡开发成本）
- 二者也可以结合，比如先用LightRAG粗筛，在用GraphRAG精炼



## 实战

### 快速上手

TODO