参考项目：[用三个笨办法将千万字的《凡人修仙传》炼成一个知识图谱](https://yage.ai/fanren.html)

制作知识图谱：

- [GraphRAG快速入门 / GraphRAG制作的《凡人修仙传》知识图谱长什么样？](https://techdiylife.github.io/blog/blog.html?category1=c01&blogid=0061)
- ~~[手把手教你用GraphRAG+Neo4j实现知识图谱可视化(凡人修仙传)](https://www.bilibili.com/video/BV1v1YezxEGM/?vd_source=35dfee2e398af56613f978fc65d6defb)~~
- ~~[【GraphRAG知识图谱】GraphRAG+知识图谱可视化--斗破苍穹，构建+检索全流程实操！](https://www.bilibili.com/video/BV1UDUbBDEED)~~
- [本地部署 Ollama+graphRAG 询问万人敬仰的韩天尊相关经历](https://github.com/wangdayaya/Learning/blob/bbf6561626414cddd417b61c8cf82d5292bbc189/%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD/%E6%9C%AC%E5%9C%B0%E9%83%A8%E7%BD%B2%20Ollama%2BgraphRAG%20%E8%AF%A2%E9%97%AE%E4%B8%87%E4%BA%BA%E6%95%AC%E4%BB%B0%E7%9A%84%E9%9F%A9%E5%A4%A9%E5%B0%8A%E7%9B%B8%E5%85%B3%E7%BB%8F%E5%8E%86.md)
- [2024-2-13graphrag](https://lilinji.github.io/2025/12/%E7%9F%A5%E8%AF%86%E5%9B%BE%E8%B0%B1/#2024-2-13graphrag)



### 示例方案

> 以下内容为大模型编写的方案

GraphRAG = 向量检索（语义） + 知识图谱（结构） + LLM 推理



#### Step0 架构概述

```
                ┌──────────┐
                │  小说原文 │
                └────┬─────┘
                     │
        ┌────────────▼────────────┐
        │  文本切分 + 信息抽取     │
        │ (实体 / 关系 / 事件)     │
        └──────┬────────┬─────────┘
               │        │
      ┌────────▼─┐  ┌──▼────────┐
      │ 向量数据库│  │ 图数据库  │
      │ (Chroma…) │  │ (Neo4j…)  │
      └─────┬─────┘  └────┬──────┘
            │              │
            └──────┬───────┘
                   ▼
            ┌──────────────┐
            │   GraphRAG   │
            │  检索 + 推理 │
            └──────┬───────┘
                   ▼
               LLM 输出
```

```
原始小说文本
    ↓
结构化切分（章节 / 场景）
    ↓
信息抽取（实体 / 关系 / 事件）
    ↓
构建小说知识图谱（Graph）
    ↓
Graph + 向量 双索引
    ↓
GraphRAG 查询与生成
```



#### Step1 文本切分

>不推荐：固定 500 token 生切
>推荐：结构感知切分

1️⃣ 按「叙事结构」切

推荐层级：Scene 是 GraphRAG 的黄金粒度

```
小说
 ├─ 卷 / 篇（如果有）
 │   ├─ 章节
 │   │   ├─ 场景（scene）
```

2️⃣ 场景切分方法

可用 LLM 辅助：Prompt 示例如下

```
请将以下章节划分为若干“场景”，每个场景需满足：

- 时间和地点相对统一
- 人物不超过 5 个
- 有明确事件或对话
```

输出结构化 JSON。



#### Step2 信息抽取

这里是你从“普通 RAG”迈入“RAG 大师”的分水岭。

------

1️⃣ 抽取三大核心对象

（1）实体（Entities）

小说常见实体类型：

| 类型 | 示例              |
| ---- | ----------------- |
| 人物 | 张无忌、哈利·波特 |
| 地点 | 霍格沃茨、长安    |
| 组织 | 门派、国家        |
| 物品 | 魔法石、宝剑      |
| 概念 | 诅咒、武功、规则  |

（2）事件（Events）

事件是小说的“发动机”。

事件包含：

- 参与者（人物）
- 地点
- 时间（相对/绝对）
- 行为
- 结果

示例：

```
Event: 哈利击败奇洛
- 参与者: 哈利, 奇洛
- 地点: 霍格沃茨地下
- 结果: 魔法石被保护
```

（3）关系（Relations）

人物关系是小说 Graph 的主干。

| 关系类型 | 示例          |
| -------- | ------------- |
| 亲属     | 父子、师徒    |
| 社会     | 同盟、敌对    |
| 情感     | 爱慕、仇恨    |
| 因果     | 因为A → 导致B |
| 隶属     | 属于某组织    |

------

2️⃣ 抽取方式（实战推荐）

✅ LLM + 结构化 Prompt

**强烈建议 JSON Schema**

示例 Prompt（简化版）：

```
从以下小说场景中抽取信息：
1. 实体（人物 / 地点 / 物品）
2. 事件
3. 实体之间的关系

请以 JSON 输出，字段必须符合 schema。
```

Schema 示例：

```
{
  "entities": [
    {"id": "E1", "type": "Person", "name": "张三"}
  ],
  "events": [
    {
      "id": "EV1",
      "description": "张三击败李四",
      "participants": ["E1", "E2"]
    }
  ],
  "relations": [
    {
      "source": "E1",
      "target": "E2",
      "type": "敌对"
    }
  ]
}
```

------

补充：

- 换句话说，此步骤是定义你的知识图谱 Schema（先设计！），主要分如下两个核心

  - 核心节点（Node Types）

    ```
    Character（人物）
    Location（地点）
    Event（事件）
    Organization / Faction（组织/阵营）
    Item（物品，可选）
    Chapter / Scene（可选，用于时间线）
    ```

  - 核心关系（Relation Types）：小说 GraphRAG 的灵魂 = Event（事件）

    ```
    (:Character)-[:KNOWS]->(:Character)
    (:Character)-[:LOVES / HATES / BETRAYS]->(:Character)
    (:Character)-[:PARTICIPATED_IN]->(:Event)
    (:Event)-[:HAPPENED_AT]->(:Location)
    (:Event)-[:CAUSES]->(:Event)
    (:Character)-[:BELONGS_TO]->(:Faction)
    (:Event)-[:OCCURRED_IN]->(:Chapter)
    ```

- 关于用 LLM 抽取实体与关系（主流方案）：推荐流程（两阶段）如下

  - 第一阶段：实体识别，Prompt 示例如下

    ```
    请从以下小说文本中提取所有明确出现的实体：
    - 人物（Character）
    - 地点（Location）
    - 组织/阵营（Faction）
    - 重要事件（Event）
    
    返回 JSON，不要解释。
    ```

  - 第二阶段：关系抽取

    ```
    基于以下文本和已识别实体，
    请抽取实体之间的关系（含时间或因果，如有）。
    
    关系需包含：
    - source
    - target
    - relation
    - evidence（原文句子）
    ```

  - 技巧：

    - 人物别名 → 用 `alias` 字段统一
    - 事件要有 `event_id`，避免重复



#### Step3 构建小说知识图谱

1️⃣ 图模型设计（重点）

节点（Node）

| Node 类型    | 说明 |
| ------------ | ---- |
| Person       | 人物 |
| Location     | 地点 |
| Event        | 事件 |
| Organization | 组织 |
| Item         | 物品 |
| Scene        | 场景 |

边（Edge）

| Edge 类型       | 含义        |
| --------------- | ----------- |
| PARTICIPATES_IN | 人物 → 事件 |
| HAPPENS_AT      | 事件 → 地点 |
| APPEARS_IN      | 实体 → 场景 |
| RELATES_TO      | 人物 ↔ 人物 |
| CAUSES          | 事件 → 事件 |

2️⃣ 推荐 Graph 数据库

| 场景   | 推荐     |
| ------ | -------- |
| 生产级 | Neo4j    |
| 云原生 | Neptune  |
| 实验   | NetworkX |
| 微服务 | ArangoDB |



#### Step 4：Graph + Vector 双索引

为什么要“双索引”？

| 问题类型         | 更适合        |
| ---------------- | ------------- |
| “谁和谁什么关系” | Graph         |
| “相似情节/描写”  | Vector        |
| “某人物的成长线” | Graph + Event |
| “某段文风/描写”  | Vector        |

具体做法

1️⃣ Vector Index

- 存：
  - Scene 文本
  - Event 描述
- 用于语义召回

2️⃣ Graph Index

- 存：
  - 实体关系
  - 事件链
- 用于逻辑推理

------

备注：向量不是替代图，而是补充！

- 存什么？

  - 原文 chunk
  - 每个 Event 的文本描述
  - 关键人物关系的摘要

- 示例：

  ```
  {
    "text": "张三在雨夜背叛了李四……",
    "metadata": {
      "type": "event",
      "event_id": "E_023",
      "chapter": 23,
      "characters": ["张三","李四"]
    }
  }
  ```

  

#### Step5 GraphRAG 查询流程

标准 GraphRAG Query Flow：

```
用户问题
  ↓
意图识别
  ↓
Graph 查询（找相关人物/事件）
  ↓
Vector 查询（补充细节文本）
  ↓
上下文重组
  ↓
LLM 生成
```

示例 1：人物关系类问题

- 问题：张三和李四为什么反目？

- Graph 查询：

  - 找二者关系
  - 找共同事件
  - 找因果链（CAUSES）

- 向量检索（语义）

  - 检索 `event_id` 对应的原文

  - 相关 Scene 细节

- LLM 综合生成

  ```
  基于事件链 + 原文证据，
  请解释张三背叛李四的原因，
  并引用对应章节。
  ```

  

