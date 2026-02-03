> 尽管当前文档中已标记较多 ✅ 项目，但其中相当一部分仍停留在基础理解或 Demo 验证层面。本阶段将聚焦于我个人求职过程中急需掌握的核心内容，其余内容暂视为阶段性完成项，在后续多轮系统复查中逐步补齐深度与细节。

TODO

- [ ] 准备面经：充电视频、Agent框架面经、Agent情景题、Agent面经、微调、Golang
- [ ] 手撕算法：手撕LLM题、Hot100



## 技术大纲

> 本项目技术路线参考企业大模型应用开发相关招聘需求整理而成，覆盖从系统设计、模型训练部署到 Agent 应用落地。

### 内容导航

- 00 InterviewExperience｜技术栈调研：跟进企业需求，是本项目纲要内容的关键来源
- 01 SoftwareSystemDesign｜系统设计：面向大模型应用开发岗位，补充后端、前端与分布式系统能力
- 02 LLM_Training_and_Deployment｜大模型微调与部署：大模型微调、推理与工程化落地
- 03 LLM_Foundation｜LLM 基础知识：各类大模型教程的学习笔记
- 04 LLM_Application_Development｜大模型应用开发：Agent、RAG 等实际应用开发能力（本项目核心）
- 05 OpenSource_Project_Analysis｜开源项目解析：对高 Star / 高关注度项目进行结构与实现分析
- 06 Others｜其他：其他零散但有价值的知识点

------

### 00 InterviewExperience｜技术栈调研

- [x]  招聘需求调研：Boss直聘、企业官网等渠道，聚焦 Agent / LLM 相关岗位
- [x] 经验资料整理：购买并整理系统化的面经与技术材料
- [x] 社区面经跟进：持续关注技术社区的面经

------

### 01 SoftwareSystemDesign｜系统设计

#### 01-1 前后端开发能力

- [x] 编程语言：以业务驱动为核心，整体方向为 一门系统语言（C++ / Go / Java）+ 一门解释型语言（Python / JavaScript）
- [x] 后端开发：精通至少一种主流后端语言（Python/Node.js/C++），开发 Agent 核心组件，具备扎实的数据结构和算法基础
  - [x] Python：作为主力语言，负责 Agent 核心逻辑与原型开发
  - [x] （Go学了基础，Rust不学了）Rust/Go (加分，go基本一二线在用，能进去就学，rust未来几年国内发展前景可能有限，不过大模型领域可能涉及): 对于需要极致性能和高并发的场景，如LLM推理服务的基础设施层，掌握Rust或Go将是重要优势。
  - [x] （10分钟快速入门了一下，暂时无需精通）Node.js : 在需要构建高并发、实时交互场景时，Node.js的掌握将是优势
  - [ ] （一般项目暂时无此需求，优先级低） C++：学习基础（熟悉模板、并发编程、性能调优，找一个LLM相关项目去做），有系统开发经验（如代码随想录 - C++ k-v分布式存储项目）
  - [x] （实现Demo）基于Python生态搭建项目原型，Go 作为 API Gateway、负载均衡器、会话管理层，负责高并发请求和云原生调度（Go做高并发 API 网关和服务编排）
  - [x] （了解概念）其他：Uvicorn、WebSocket、SocketIO
- [x] 前端开发：
  - [x] 语言基础：JavaScript / TypeScript
  - [x] 框架：React / Vue（偏向 React，用于 LLM 应用）
  - [ ] 工具链：Webpack / Vite，状态管理 Redux / MobX
- [x] 数据库开发：MySQL、Redis、MongoDB 等常见数据库与缓存方案


------

#### 01-2 微服务与分布式系统

近几年云业务营收不错，大厂也在增强云业务：

- [x] （啥也不会） 微服务与分布式系统资料调研
- [ ] 熟悉微服务架构，掌握容器化技术（Docker/K8s），具备 DevOps 流水线建设经验
  - [x] （跑通了Demo）Docker：精通 Docker 容器化技术，能编写高效的Dockerfile
  - [x] （跑通了Demo）Kubernetes：理解核心概念（Pod、Deployment、Service、Ingress、Volume等），具备在生产环境中部署和管理微服务的经验
  - [ ] 服务治理：支持灰度发布、回滚，P99 < 100ms
  - [ ] 自研 sidecar 做动态配置、热升级，单集群 100+ 微服务、CPU 利用率>60%，写过 CRDT 或分布式事务
- [ ] 分布式中间件与组件
  - [x] （啥也不会）熟悉分布式系统、微服务架构、消息队列（如Kafka, RabbitMQ）和数据库（SQL/NoSQL）
  - [x] 熟悉服务间通信机制（REST/gRPC/WebSocket）、服务注册与配置中心（Consul/Nacos）
  - [x] 了解FastAPI（关注一下fastapi and pydantic、Resful API）, ES, MongoDB, Kafka, Clickhouse等常用技术组件，了解协程、缓存、消息、搜索、微服务等后端常用技术
  - [x] 了解分布式存储系统（如Mooncake Store、Milvus、Redis、FAISS），熟悉缓存策略与数据分片
- [ ] 有大规模系统（千节点级）调优或调度系统开发经验优先；熟悉分布式一致性、负载均衡、限流熔断等高可用架构设计理念

------

#### 01-3 性能优化与系统调优

- [x] （这些工具都偏向C++开发，暂时没用上）掌握 Linux 环境开发、性能分析工具使用（perf, strace, gdb, valgrind, nsight, vtune）
- [ ] （跑通了Demo）Python内存管理：能进行内存泄漏排查、IO/CPU瓶颈定位，理解协程调度、事件驱动模型
- [ ] （有一个任务需要做）有使用 Nginx/Uvicorn/Gunicorn 等高并发网关部署经验
- [ ] 服务网格 Service Mesh：涉及API服务部署、管理、监控，可以在高并发网关部署项目中直接应用。了解或实践过 Istio、Linkerd 等服务网格技术，用于实现流量管理、可观测性和安全性
- [x] 项目实战：[FastAPI 性能进化：如何实现百万请求](https://mp.weixin.qq.com/s/gUyq14FTLPWj7IdAV28Z5A)、[FastAPI Ultra：让 Uvicorn、uvloop 与 Pydantic v2 飞起来](https://mp.weixin.qq.com/s/h65xB89bmhTF5zKdt3F3KA)


------

### 02 LLM_Training_and_Deployment｜大模型微调与部署

#### 02-1 推理与部署

- [x] 有大语言模型（如BERT、GPT系列等）的后端服务化部署案例者优先；
- [x] 熟悉 LLM推理框架（如vLLM、SGLang），理解KV Cache、PagedAttention等核心机制
  - [x] （了解了概念，未实践）实现 Continuous Batching + PagedAttention，单机吞吐提升 4×
  - [x] （学不了一点）掌握 调度算法（如动态批处理、连续批处理、抢占式调度），有Scheduler开发经验。自研 Scheduler 支持抢占/回填，千卡集群 GPU 利用率>75%

- [x] （只知道调整部署框架的参数，如vllm）负责LLM模型算法的工程化落地，包括但不限于算法逻辑工程化，节点级multi session的管理及调度来支持高并发，对外提供统一的API
- [x] （跑通了Demo）模型量化: 了解int8、fp8、AWQ、GPTQ 等量化技术，并能将其应用于模型推理端，以降低模型大小和显存占用，提高推理速度

------

#### 02-2 训练与对齐

- [x] （跑通了Demo）训练：熟悉 SFT 流程及 LoRA、QLoRA、PEFT 等参数高效微调技术
- [x] （显存要求太高，玩不起）verl：掌握强化学习对齐技术（PPO、DPO、RRHF、GRPO 等）
- [ ] 有训练脚本开发经验：使用过 Transformers、Deepspeed、FSDP、Megatron-LM等训练框架
- [x] 能进行模型评估与对比实验：掌握 BLEU/ROUGE/MMLU/BioASQ 等测评指标
- [ ] （Agent下一阶段的重点可能在数据构建与评估上）熟悉数据清洗与样本构造，理解对齐数据的重要性与构建技巧

------

### 03 LLM_Foundation｜LLM 基础

- [x] LLM系统知识：
  - [x] 《从零开始构建大语言模型》教材和代码，以及一些对其解读的项目
  - [x] （听不懂，暂缓）karpathy大神gpt-2复现等系列课程，非常细节
  - [x] （听不懂，暂缓）CS336：比较深入，放最后学
  - [x] （听不懂，暂缓）结合Chaofa大佬的课程：手撕代码、ZeroHero、动手学习大模型
  - [x] （直接看官方文档）AIInfra：ZOMI的AI Infra系列教程，快速补充一些概念
- [x] LLM八股：
  - [x] （了解了概念，未实践）具备良好的模型评估和优化能力，能够使用各种指标和方法来衡量模型的性能和效果，如准确率、召回率、BLEU、ROUGE等；
  - [x] （持续积累中）NLP基础知识：常用知识点、注意力、隐马尔可夫、常用损失函数、常用优化函数、池化、标准化等等
  - [x] （持续积累中）LLM基础知识：先系统学习八股，之后根据各类付费资料包、面经、推文持续补充
- [x] （了解了概念，未实践）其他方向：推荐系统、具身智能、数学建模、扩散模型
- [x] （持续积累中）手搓系列：Transformer、nanoGPT等

------

### 04 LLM_Application_Development｜大模型应用开发

#### 04-1 基础框架与应用

- [x] （跑通了Demo）熟练使用 OpenAI SDK、LangChain、LlamaIndex、AutoGPT、MetaGPT 等 LLM 应用框架
- [x] （了解了概念，未实践）对LLM的应用场景（如智能客服、智能运维、智慧搜索）有实际落地经验优先
- [x] （了解了概念，未实践）熟悉 “Ambient Agent UX” 理念，具备优秀的交互设计意识

------

#### 04-2 Agent 架构与推理机制

- [x] LLM核心机制与设计原则：
  - [x] 深入理解 LLM Agent 系统结构，熟悉核心机制：Planning、Execution、Memory、Tool Use；掌握 function calling 机制，具备复杂工具集成与函数路由能力
  - [x] 熟悉 ReAct、CoT、ToT、Self-Ask 等范式
  - [x] 设计原则：How to Build Reliable AI Agents，参考12-Factor Agents、7 Building Blocks、Anthropic等资源

- [x] Agent开发框架：主要就是OpenAI Agent SDK、LangChain
  - [x] （跑通了Demo）LangGraph：设计多Agent协同任务流
  - [x] （跑通了Demo）OpenAI Agents SDK：包含单代理、多代理（routing、agents_as_tools等）相关代码
  - [x] （跑通了Demo）A2A协议
  - [x] （跑通了Demo）其他：CrewAI、LangChain-DeepAgents、smolagent

- [x] 上下文工程：
  - [x] （跑通了Demo）Prompt/Context Engineering等技巧
  - [x] （跑通了Demo）Mem0、LLMLingua等框架

- [x] （跑通了Demo）监测工具：熟悉LangSmith、LangFuse、PromptLayer等链路监控与调优工具，具备提示词迭代与质量优化经验
- [x] （跑通了Demo）执行环境：Sandbox、E2B等

------

#### 04-3 RAG 系统开发

- [x] 基础概念：
  - [x] （跑通了Demo）熟悉 RAG 系统全链路开发：内容解析（parsing）、切分策略（chunking）、向量化（embedding）、检索（retrieval）、排序（ranking & reranking）
  - [x] （跑通了Demo）熟悉向量数据库（FAISS、Chroma、Milvus、Weaviate）原理与选型
  - [x] （了解了概念，未实践）掌握 hybrid retrieval 技术（稀疏+稠密），了解 ColBERT、BM25、TART 等前沿方法
  - [x] （了解了概念，未实践）了解 RAG 2.0 架构，具备构建多源异构知识集成能力者优先
  - [x] （了解了概念，未实践）Agentic RAG
- [x] 开发框架及实践：
  - [x] （了解了概念，未实践）能基于 LangChain、LlamaIndex 构建 RAG pipeline，支持动态检索源扩展与知识版本管理
  - [x] （跑通了Demo）GraphRAG：项目实践
  - [x] （了解了概念，未实践）LightRAG框架


------

### 05 OpenSource_Project_Analysis｜开源项目解析

- [x] 通用智能体类：
  - [x] OpenHands：原OpenDevin，对标软件助手Devin，Manus像是Devin的通用智能版
  - [x] OpenManus：复现Manus的玩具
  - [x] Suna：Manus名字倒过来
  - [x] DeerFlow：跟Suna的DeepResearch似乎有关系
  - [x] 其他：Parlant、ByteBot等
- [x] VibeCoing类
  - [x] ClaudeCode：以及SpecKit
  - [x] Kobe
  - [x] Trea


- [ ] 场景分析：客服、运维、搜索、金融等


------

### 06 Others

常用：

- [x] Vibe Coding 工具：Cursor、ClaudeCode

- [x] 基础工程能力：Git、Docker等
- [ ] 软技能：1）有一双发现垃圾的眼睛，能喷人，也接受被喷；2）沟通能力强，能与算法、产品、运营、老板对话，把技术价值翻译成牛鬼蛇神都能理解的语言；3）沟通能力、协作能力、复杂问题拆解能力、完整的方法论、向上汇报能力、甩锅能力

加分项：

- [ ] GPU 架构理解: 深入理解 GPU 架构（如 NVIDIA Ampere、Hopper），了解 SM、warp、register、shared memory 等概念，以便进行更底层的性能优化
- [ ] CUDA/Triton 开发: 具备 CUDA 编程经验，能够编写高效的 GPU 内核，或使用 Triton 框架自定义高性能算子，参考 https://www.bilibili.com/video/BV1zzNmzfEnF
