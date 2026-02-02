## Summery

涉及到模型部署：

- GPU方案：vLLM、SGLang
- CPU方案：llama.cpp

- 特殊方案：Ktransformer

详细内容，可参考本目录相关笔记



## Others

### 零零碎碎

> 参考：[大模型推理必看！2025最值得读的14篇论文和2篇博客](https://mp.weixin.qq.com/s/dg8FGNZ0mZOxF4b5fwUxkw)

TODO



> 参考：[LLM推理框架学习笔记](https://mp.weixin.qq.com/s/fJ8ElrDfaC7ekqcNTd9paA)

一些基础概念 + 几种并行/分布式策略

- **概念**
  - 连续批处理
  - 页式注意力
  - 量化
  - 硬件优化
- **分布式推理策略**
  - 张量并行(Tensor Parallelism)：把模型的权重（如线性层的矩阵）沿某个维度（行或列）切分，分配到不同的GPU上
  - 流水线并行 (Pipeline Parallelism)：将大模型的多层结构按层切分，分配到不同的设备（如 GPU）上。每个设备只负责模型的一部分层。数据（如输入序列）像“流水线”一样依次流经这些设备，逐段完成计算。
  - 数据并行（Data Parallelism）：在多张显卡上部署多个一模一样的模型，当一次性要处理多个用户请求时，可以将这些请求平均分配给不同的GPU处理，最后再把不同GPU处理得到的结果合并后输出
  - 将上述的几种策略进行组合
- **主要的量化技术**
  - GPTQ
  - AWQ
  - GGUF/GGML



> 参考：[LLM 推理引擎选型指南：Transformers、llama.cpp 与 vLLM 该怎么选？](https://mp.weixin.qq.com/s/ODIJ2IApGluAhC-76UdEow)

概述了 Transformers、llama.cpp 与 vLLM ，简要补充些概念应对面试：

- Transformers：解释型语言般的通用基准
  - 核心机制：Eager Execution (动态图)
  - 内存模型：连续分配的痛点（其性能瓶颈往往不在于“内存对齐”，而在于 KV Cache 的连续内存分配策略）
  - 适用场景：代码验证与原型开
- llama.cpp：嵌入式思维下的“裸机”优化
  - 核心技术：量化 (GGUF) 与 内存墙突破
  - 计算优化：异构加速与 SIMD
  - 适用场景：端侧部署
- vLLM：引入操作系统的“分页内存管理”
  - 架构创新：PagedAttention
  - 性能表现：Continuous Batching
  - 适用场景：生产级高吞吐 API
- 其他：
  - 算子编程与中间件 Triton (语言/编译器)：由 OpenAI 开发，它不是 vLLM 的附属，而是一种类似 Python 的 GPU 编程语言
  - 复杂调度与 Agent 优化 SGLang (结构化与缓存)：
    - Radix Attention：基于前缀树（Radix Tree）管理 KV Cache，实现了跨请求的 Prompt 缓存（自动识别并缓存多轮对话或 Agent 任务中的公共前缀）
    - 结构化生成：原生支持强制模型输出符合 JSON Schema 或 Regex 格式，非常适合工具调用（Function Calling）场景
  - 异构与国产化
    - KTransformers (异构卸载)：将模型的冷数据（如部分权重）Swap 到 CPU 内存，热数据留在 GPU
    - 华为 MindIE (硬件抽象)：华为昇腾（Ascend）硬件的专用运行时。它底层对接 CANN（对标 CUDA），针对 NPU 的 Cube Unit 进行了深度优化



### 节点级 multi-session 管理 & 调度

> （“模型落地”相关招聘要求）关于 **节点级 multi-session 管理 & 调度** 设计，以下为大模型给出的方案，供参考

目标摘要：

- 支持“一个节点上同时托管多个 session（multi-session）”并发交互
- 支持模型复用、微批（micro-batching）、优先级、公平调度、预取/热启动与会话隔离
- 与 vLLM（高效批推理）及 LangChain（任务/chain 编排）兼容
- 节点级本地调度 + 全局调度（集群级）协同

------

#### 1、总体架构（高层）

1. **Ingress / API 网关**（HTTP/gRPC/WS）
   - 接收用户请求（会话创建、推理请求、流式输出）
   - 身份认证、速率限制、路由到 Global Scheduler
2. **Global Scheduler（全局）**
   - 维护集群资源视图（每个节点：GPU/CPU/内存/已加载模型/会话数/队列长度）
   - 负责会话放置（placement）、负载均衡、跨节点迁移决策
   - 提供策略：最少负载、bin-packing、优先级/隔离/租户策略
3. **Node Agent（每节点）**
   - **Session Manager（节点级）**：管理本节点上的 N 个 session（multi-session）
   - **Model Pool / Loader**：负责模型加载、卸载、共享（单副本多会话）、模型缓存
   - **vLLM Runtime Adapter**：与 vLLM 的 batch API 集成（收集 micro-batches）
   - **Execution Worker Pool**：处理 CPU 前处理、后处理与与模型的异步交互
   - **Local Scheduler**：接收 Global Scheduler 的放置命令或直接从 ingress 获取请求（预留）
   - **Metrics & Health**：上报 Prometheus / OTLP
4. **State Store / Metadata**（etcd / Redis / Postgres）
   - 会话元信息、模型元数据、冷启动槽位、迁移状态
   - 支持快速读取的会话路由表（gateway -> scheduler -> node）
5. **Control Plane / Operator（可选，K8s operator）**
   - 管理节点扩缩、模型镜像、作业生命周期
6. **Observability & Tracing**
   - Prometheus + Grafana + Jaeger
   - 关键指标：latency p50/p95/p99、GPU util、batch size、ctx reuse ratio、queue length

------

#### 2、节点级 multi-session 管理（详细）

**1）会话生命周期**

- CreateSession(user, model, config)：
  - Check quota/tenant limits → allocate session_id → decide placement via Global Scheduler
  - Node Agent 在 Model Pool 中确保目标模型已加载（或触发异步加载），为 session 分配 `SessionContext`（包括 max_tokens、priority、warmup_flags）
- HandleRequest(session_id, request)：
  - Local Session Manager 根据 request 类型（sync/stream）入本地队列
  - Local Scheduler 决定放入 micro-batching 集合或立即处理（低延迟优先）
- CloseSession(session_id)：
  - 清理 context（可选持久化短期历史），减少会话计数
  - 若模型冷却策略命中，释放模型资源或降级 warm-pool
- MigrateSession(session_id, dest_node)（可选）：
  - Serialize minimal session state（context pointers or embeddings）到 State Store
  - 在目标节点恢复会话并切换路由表；源节点停止接收新请求，完成尾部请求后移除

**2）数据结构（Python 风格示例）**

```python
class SessionContext:
    session_id: str
    model: str
    user_id: str
    priority: int
    max_tokens: int
    token_history_ptr: Optional[str]  # pointer to external cache if large
    state: dict  # ephemeral metadata, e.g., running streaming cursor
    node_id: str  # current placement

class NodeResource:
    node_id: str
    gpus: List[GPUInfo]
    cpu_cores: int
    gpu_free_mem: Dict[int, int]
    models_loaded: Set[str]
    session_count: int
    queue_len: int
```

**3）本地队列与微批（micro-batching）**

- Local Session Manager 维护多个优先级队列（p0..pn），以及一个 `Batcher` 进程：
  - 每个 tick（例如 1–10ms）收集同 model 的请求，按 tokens/latency/priority 打包成 batch，交给 vLLM。
  - batch size 上限依据 GPU memory 动态计算（或 vLLM 提供的 API）。
- 对低延迟请求，支持 `eager_cutoff`（若等待超过 L ms 则立即揽入当前 batch）。
- 对流式请求，拆分为小 batch 或单独 stream 路径（保证低延迟）。

**4）vLLM 集成点（实践要点）**

- 使用 vLLM 的批处理接口（e.g., `model.generate_batch(prompts)`），并配合其 token-level streaming（若支持）。
- vLLM 通常会管理 GPU 内存池、并提供高吞吐微批策略：把 Local Batcher 的待处理 batch 变为 vLLM 的 batch。
- 重要：vLLM 对显存要求高，建议：
  - 共享一份 model 副本给多个 session（避免每 session 都加载）
  - 使用 vLLM 的 quantization / mixed precision 支持（如 4/8-bit）
  - 为不同优先级设定显存配额或 QoS（避免低优先级抢占）

------

#### 3、调度策略（全球 + 节点级）

1）全局（Global Scheduler）

- **输入**：会话创建请求（model, priority, tenant）, cluster resource snapshot

- **目标函数**（示例）：

  ```python
  score(node) = w1 * free_gpu_mem_ratio + w2 * (1 - queue_len_norm)
              + w3 * model_loaded(node, model) + w4 * session_affinity_bonus
  choose node with max(score)
  ```

- 支持策略切换：低延迟优先 / 成本最优 / 隔离模式

- 支持模型分层（hot/warm/cold）：

  - Hot: 常驻 GPU，在多个节点保留副本
  - Warm: 可快速加载（缓存）
  - Cold: S3 存储，按需加载

2）节点级（Local Scheduler）

- 负责微批调度、优先级队列、速率限制、token 带宽分配
- 对同一 model 的 requests 优先打包；对跨模型则隔离 batch

3）公平与优先级

- 使用多级反馈队列（MLFQ）或令牌桶来保证公平与QoS
- 高优先级请求（如对话交互）设置短等待上限并可 preempt（中断低优先级 batch）
- 低优先级批处理走 background queue（尽量大批以提高吞吐）



示例代码结构：整个实现为 **可运行的 Python/FastAPI + Redis** 版本

```
global_scheduler/
  ├── scheduler.py        # GlobalScheduler 主类
  ├── models.py           # 数据结构：NodeInfo, SessionMetadata
  ├── storage.py          # Redis 后端 - 元信息存储
  ├── api.py              # FastAPI 接口入口（/v1/sessions/create）
  └── strategy/
        └── placement.py  # 节点选择策略
```



📌 **1. `models.py` — 数据模型定义**

```
from pydantic import BaseModel
from typing import Dict, Optional, List


class NodeInfo(BaseModel):
    node_id: str
    address: str
    gpu_free_mem: int
    gpu_total_mem: int
    running_sessions: int
    loaded_models: List[str]
    queue_len: int
    last_heartbeat_ts: float


class SessionMetadata(BaseModel):
    session_id: str
    model: str
    user_id: Optional[str] = None
    node_id: Optional[str] = None
    priority: int = 5
    created_ts: float = 0.0
```



📌 **2. `storage.py` — Redis 存储层**

```
import time
import json
import redis
from typing import Dict, List, Optional
from models import NodeInfo, SessionMetadata


class RedisStore:
    def __init__(self, url="redis://localhost:6379/0"):
        self.r = redis.from_url(url)

    ############################################################
    # Node Info
    ############################################################
    def get_all_nodes(self) -> List[NodeInfo]:
        keys = self.r.keys("node:*")
        result = []
        for k in keys:
            data = json.loads(self.r.get(k))
            result.append(NodeInfo(**data))
        return result

    def save_node(self, node: NodeInfo):
        self.r.set(f"node:{node.node_id}", node.json())

    ############################################################
    # Session Info
    ############################################################
    def save_session(self, session: SessionMetadata):
        self.r.set(f"session:{session.session_id}", session.json())

    def get_session(self, session_id: str) -> Optional[SessionMetadata]:
        data = self.r.get(f"session:{session_id}")
        return SessionMetadata(**json.loads(data)) if data else None

    def update_session_node(self, session_id: str, node_id: str):
        s = self.get_session(session_id)
        if not s:
            return
        s.node_id = node_id
        self.save_session(s)
```



📌 **3. `strategy/placement.py` — 节点调度策略**

> 核心：
>
> - 优先选 **已加载目标模型** 的节点（减少冷启动）
> - session affinity（如果 session 已绑定节点）
> - 节点负载（queue_len / running_sessions）
> - GPU 剩余显存

```
from typing import List
from models import NodeInfo, SessionMetadata


def score_node(node: NodeInfo, session: SessionMetadata) -> float:
    """节点打分函数，可根据需要扩展"""

    # 模型是否已加载
    model_loaded_bonus = 1.0 if session.model in node.loaded_models else 0.0

    # 负载指标（任务越少越好）
    load_factor = (node.queue_len + node.running_sessions) + 1

    # GPU 空闲比例
    gpu_free_ratio = node.gpu_free_mem / max(node.gpu_total_mem, 1)

    return (
        3.0 * model_loaded_bonus +
        2.0 * gpu_free_ratio +
        1.0 / load_factor
    )


def choose_best_node(nodes: List[NodeInfo], session: SessionMetadata) -> NodeInfo:
    """根据评分找到最优节点"""
    ranked = sorted(nodes, key=lambda n: score_node(n, session), reverse=True)
    return ranked[0]
```



📌 **4. `scheduler.py` — Global Scheduler 主逻辑**

```
import time
import uuid
from typing import Optional
from storage import RedisStore
from models import SessionMetadata, NodeInfo
from strategy.placement import choose_best_node


class GlobalScheduler:

    def __init__(self, store: RedisStore):
        self.store = store

    ####################################################################
    # Create a new session and find node placement
    ####################################################################
    def create_session(
        self,
        model: str,
        user_id: str,
        priority: int = 5,
        session_id: Optional[str] = None
    ) -> SessionMetadata:

        session_id = session_id or str(uuid.uuid4())
        session = SessionMetadata(
            session_id=session_id,
            model=model,
            user_id=user_id,
            priority=priority,
            created_ts=time.time(),
        )

        nodes = self.store.get_all_nodes()
        if not nodes:
            raise RuntimeError("No available nodes for scheduling")

        # 按策略找节点
        best_node = choose_best_node(nodes, session)

        # 记录 session → node 映射
        session.node_id = best_node.node_id
        self.store.save_session(session)

        return session

    ####################################################################
    # 查询已有 session 应放置的节点（用于路由）
    ####################################################################
    def route_session(self, session_id: str) -> str:
        session = self.store.get_session(session_id)
        if not session:
            raise ValueError("Session not found")
        if not session.node_id:
            raise ValueError("Session is not assigned yet")
        return session.node_id
```



📌 **5. `api.py` — FastAPI 对外接口**

你可以将该 API 部署为“全局调度服务”。

```
import uvicorn
from fastapi import FastAPI, HTTPException
from storage import RedisStore
from scheduler import GlobalScheduler

app = FastAPI()
store = RedisStore()
scheduler = GlobalScheduler(store)


class CreateSessionReq(BaseModel):
    user_id: str
    model: str
    priority: int = 5


@app.post("/v1/sessions/create")
def create_session(req: CreateSessionReq):
    try:
        sess = scheduler.create_session(
            model=req.model,
            user_id=req.user_id,
            priority=req.priority,
        )
        return {
            "session_id": sess.session_id,
            "node_id": sess.node_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/sessions/{session_id}/route")
def route_session(session_id: str):
    try:
        node = scheduler.route_session(session_id)
        return {"node_id": node}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
```



📌 6. Global Scheduler 的关键特性（已包含）

- ✔ **session → node 映射缓存**
- ✔ **模型热度感知（已加载模型优先）**
- ✔ **负载均衡（queue_len / session_count）**
- ✔ **GPU 显存权重**
- ✔ **session affinity**
- ✔ **可扩展打分策略**
- ✔ **支持 Redis 集群模式**



📌 7. 如何与 Node Agent 结合？

Node Agent 定期上报：

```
POST /v1/node/heartbeat
{
  "node_id": "...",
  "address": "...",
  "gpu_free_mem": 20000,
  "gpu_total_mem": 40000,
  "queue_len": 3,
  "running_sessions": 12,
  "loaded_models": ["gpt-4o-mini", "llama3-8b"]
}
```

Global Scheduler 接收并写入 Redis（store.save_node(node)），就可以让节点参与资源池。



📌 8. 如何与 LangChain Wrapper 连接？

你的 LangChain Wrapper 只需要通过：获取 session 所在节点

```
GET /v1/sessions/{session_id}/route
```

然后将所有 LLM 请求路由到返回的 node 地址即可。

------

#### 4、会话隔离与上下文管理

- 上下文保存在 **SessionContext**，对长对话采用**外部持久化（Redis/Vector DB）**，只在内存中保留 sliding window（e.g., last 2048 tokens）
- 对于 memory-heavy 功能（如工具调用、检索增强）：
  - 把长期记忆/embeddings 存在 vector DB（e.g., Milvus, Pinecone），请求时检索并作为 prompt 片段
- 采用 **prompt chunking + chunk cache**，对重复检索进行缓存

------

#### 5、会话迁移与故障恢复

- **优先方案**：尽量避免频繁迁移（session affinity），只有在节点过载或维护时迁移
- 迁移步骤：
  1. Global Scheduler 下达迁移命令
  2. 源节点将 session 的 minimal state（recent tokens，buffers）写入 State Store（可压缩）
  3. 目标节点从 State Store 读取并恢复 session；Global Scheduler 更新路由表
  4. 源节点在完成 inflight 请求后释放资源
- 故障恢复：节点突降（OOM/掉线）时，Global Scheduler 将 session 标记为 `orphaned` 并触发迁移/重建；对于有持久化的 session，上下文可以重新加载

------

#### 6、典型 API 设计（REST/gRPC）

- `POST /v1/sessions` -> 创建会话（返回 session_id, node）
- `POST /v1/sessions/{id}/messages` -> 发送请求（支持 streaming via websocket）
- `GET /v1/sessions/{id}/state` -> 查询状态
- `DELETE /v1/sessions/{id}` -> 关闭
- `GET /health`，`GET /metrics`

示例请求字段：

```python
{
  "model": "gpt-4o-mini",
  "priority": 10,
  "max_tokens": 1024,
  "stream": true,
  "tenant_id": "team-abc"
}
```

------

伪代码：Node Session Manager + Batcher（核心逻辑）

```python
import asyncio
from collections import defaultdict, deque
from time import time

class LocalBatcher:
    def __init__(self, model_name, vllm_adapter, tick_ms=5, max_batch_tokens=8192):
        self.model = model_name
        self.vllm = vllm_adapter
        self.queues = defaultdict(deque)  # priority -> deque of (session, request)
        self.tick_ms = tick_ms / 1000

    async def submit(self, session_ctx, request, priority=5):
        self.queues[priority].append((session_ctx, request))

    async def run(self):
        while True:
            batch = []
            batch_tokens = 0
            start = time()
            # collect from high->low priority
            for p in sorted(self.queues.keys()):
                q = self.queues[p]
                while q and batch_tokens < MAX_TOKENS:
                    session, req = q.popleft()
                    est = estimate_tokens(req)
                    if batch_tokens + est > MAX_TOKENS:
                        # put back for next round
                        q.appendleft((session, req))
                        break
                    batch.append((session, req))
                    batch_tokens += est

            if batch:
                # transform to vLLM batch and call
                prompts = [prepare_prompt(s, r) for s,r in batch]
                outputs = await self.vllm.generate_batch(prompts)
                # dispatch outputs back to sessions
                for (session, req), out in zip(batch, outputs):
                    session.on_response(req, out)
            # sleep until next tick or when small wait triggered
            await asyncio.sleep(self.tick_ms - (time()-start) if time()-start < self.tick_ms else 0)

```

------

#### 7、与 LangChain 的集成

- LangChain 主导上层编排（chains, agents, tools）。将 LLM 调用替换为向调度服务发出的 HTTP/gRPC 请求：
  - 写一个 `LLMWrapper`（LangChain 的 `BaseLLM`），内部把请求发送到我们的调度 API，并支持流式响应转 callback。
- 对长链路（tool calls、retrieval）：
  - 在 chain 中显式声明是否需要“低延迟模式”（interactive）或“batch mode”（background）
- LangChain 的并行化（map/async）可以被调度服务视为低优先级 batch 作业，交由 background queue 处理

示例代码：

```python
from __future__ import annotations
import json
import httpx
from typing import Any, Dict, List, Optional, Iterator

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
    AIMessage,
)
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.callbacks.manager import CallbackManagerForLLMRun

##############################################################
#                       Transport Layer
##############################################################

class SchedulerLLMTransport:
    """HTTP client for the Scheduler LLM Service."""

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

        self.client = httpx.Client(
            timeout=timeout,
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
        )

    def _messages_to_payload(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        """Convert LangChain messages -> 调度服务支持的结构."""
        result = []
        for m in messages:
            if isinstance(m, HumanMessage):
                result.append({"role": "user", "content": m.content})
            elif isinstance(m, SystemMessage):
                result.append({"role": "system", "content": m.content})
            elif isinstance(m, AIMessage):
                result.append({"role": "assistant", "content": m.content})
            else:
                raise ValueError(f"Unsupported message type: {type(m)}")
        return result

    ##############################################################
    #               Sync / Non-streaming request
    ##############################################################
    def chat(self, session_id: str, messages: List[BaseMessage], **kwargs) -> str:
        payload = {
            "session_id": session_id,
            "messages": self._messages_to_payload(messages),
            "stream": False,
            **kwargs,
        }

        resp = self.client.post(f"{self.base_url}/v1/chat/completions", json=payload)
        resp.raise_for_status()

        data = resp.json()
        return data["output"]

    ##############################################################
    #               Streaming request (server-sent events)
    ##############################################################
    def chat_stream(self, session_id: str, messages: List[BaseMessage], **kwargs) -> Iterator[str]:
        payload = {
            "session_id": session_id,
            "messages": self._messages_to_payload(messages),
            "stream": True,
            **kwargs,
        }

        with self.client.stream(
            "POST", f"{self.base_url}/v1/chat/completions", json=payload
        ) as resp:
            resp.raise_for_status()

            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except Exception:
                    continue

                if "delta" in event:  # Streaming delta token
                    yield event["delta"]


##############################################################
#                       LangChain Wrapper
##############################################################

class SchedulerChatModel(BaseChatModel):
    """
    LangChain ChatModel wrapper for LLM Scheduler.
    """

    def __init__(
        self,
        base_url: str,
        session_id: str,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        streaming: bool = False,
        timeout: int = 120,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.session_id = session_id
        self.streaming = streaming
        self.model = model
        self.transport = SchedulerLLMTransport(base_url, api_key, timeout)

    ##############################################################
    #                LangChain Core Implementation
    ##############################################################

    @property
    def _llm_type(self) -> str:
        return "scheduler_chat_model"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs
    ) -> ChatResult:

        # streaming mode
        if self.streaming:
            final_text = ""
            for token in self.transport.chat_stream(self.session_id, messages, model=self.model):
                final_text += token
                if run_manager:
                    run_manager.on_llm_new_token(token)
            return ChatResult(
                generations=[ChatGeneration(message=AIMessage(content=final_text))]
            )

        # non-streaming
        output = self.transport.chat(self.session_id, messages, model=self.model)
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=output))]
        )

```

使用示例：

- 初始化 Wrapper

  ```python
  from scheduler_llm import SchedulerChatModel
  
  llm = SchedulerChatModel(
      base_url="https://YOUR_SCHEDULER_URL",
      session_id="session-abc123",
      model="gpt-4o-mini",
      streaming=False,
  )
  ```

- 在 LangChain 中对话（非流式）

  ```python
  result = llm.invoke("给我介绍一下你是什么模型？")
  print(result.content)
  ```

- 流式对话

  ```python
  llm_stream = SchedulerChatModel(
      base_url="https://YOUR_SCHEDULER_URL",
      session_id="session-xyz999",
      streaming=True,
  )
  
  for chunk in llm_stream.stream("讲个笑话"):
      print(chunk, end="", flush=True)
  ```

------

Node Agent（节点代理）整体结构

```
node_agent/
  ├── agent.py               # NodeAgent 主入口
  ├── session_manager.py     # 会话管理（创建/绑定/状态）
  ├── local_scheduler.py     # 本地调度器（优先级队列/Micro-Batching）
  ├── vllm_adapter.py        # vLLM 推理接口
  ├── worker.py              # 执行推理任务（batch worker）
  ├── heartbeat.py           # 向全局调度器上报资源
  ├── models.py              # 数据结构
  └── api.py                 # FastAPI: /v1/chat/completions
```

🧩 1. 数据结构（models.py）

```
from pydantic import BaseModel
from typing import List, Optional


class InferenceRequest(BaseModel):
    session_id: str
    messages: List[dict]
    model: str
    stream: bool = False


class InferenceResponse(BaseModel):
    output: str


class SessionContext(BaseModel):
    session_id: str
    model: str
    last_access_ts: float
```

------

🧩 2. Session Manager（session_manager.py）

负责：

- Session 是否属于本节点
- Session 是否需要绑定模型
- 更新 last_access time（用于 LRU 或 eviction）
- 与 Global Scheduler 的 session 绑定保持一致

```
import time
from typing import Dict
from models import SessionContext


class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, SessionContext] = {}

    def ensure_session(self, session_id: str, model: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionContext(
                session_id=session_id,
                model=model,
                last_access_ts=time.time(),
            )
        else:
            self.sessions[session_id].last_access_ts = time.time()

        return self.sessions[session_id]
```

------

🧩 3. vLLM Adapter（vllm_adapter.py）

将 batch 输入转给 vLLM 实例。

```
from typing import List
from vllm import LLM, SamplingParams


class VLLMAdapter:
    def __init__(self, model_path: str):
        self.llm = LLM(model=model_path)

    def run_batch(self, prompts: List[str], max_tokens=256) -> List[str]:
        params = SamplingParams(max_tokens=max_tokens)
        outputs = self.llm.generate(prompts, sampling_params=params)
        return [out.outputs[0].text for out in outputs]
```

------

🧩 4. Local Scheduler（local_scheduler.py）

> 这是 Node Agent 的核心：
>
> - 维护多个优先级队列
> - 收集 micro-batches
> - 提交给 Worker 执行
> - 可支持并行 worker

```
import asyncio
from collections import defaultdict, deque
from typing import List, Tuple
from models import SessionContext


class LocalScheduler:

    def __init__(self, vllm_adapter, max_batch_tokens=4096, tick_ms=10):
        self.vllm = vllm_adapter
        self.queues = defaultdict(deque)  # priority -> deque[(session, message)]
        self.max_batch_tokens = max_batch_tokens
        self.tick_ms = tick_ms / 1000
        self.loop = asyncio.get_event_loop()

    async def submit(self, session: SessionContext, message: dict, priority: int = 5):
        self.queues[priority].append((session, message))

    async def run(self):
        """Batch Loop"""
        while True:
            batch_sessions = []
            batch_prompts = []
            total_tokens = 0

            # 按优先级收集 batch
            for p in sorted(self.queues.keys()):
                q = self.queues[p]
                while q:
                    session, req = q[0]
                    prompt = self._messages_to_prompt(req["messages"])

                    est_tokens = len(prompt)  # 简化估计，可完善
                    if total_tokens + est_tokens > self.max_batch_tokens:
                        break

                    q.popleft()
                    batch_sessions.append(session)
                    batch_prompts.append(prompt)
                    total_tokens += est_tokens

            if batch_prompts:
                outputs = await self.loop.run_in_executor(
                    None, self.vllm.run_batch, batch_prompts
                )
                # 把输出写回 session（这里只做示例）
                for s, out in zip(batch_sessions, outputs):
                    s.last_output = out

            await asyncio.sleep(self.tick_ms)

    def _messages_to_prompt(self, messages):
        return "\n".join([f"{m['role']}: {m['content']}" for m in messages])
```

------

🧩 5. Worker（worker.py）

如果将复杂逻辑解耦为 worker，可以这样：

```
# 用 run_batch 即可，无需单独模块
```

Node Agent 简化 worker — 因 vLLM 已异步化

------

🧩 6. Heartbeat（heartbeat.py）

定期向全局调度器上报节点资源：

```
import time
import psutil
import requests

class Heartbeat:
    def __init__(self, scheduler_url, node_id, agent_ref):
        self.scheduler_url = scheduler_url
        self.node_id = node_id
        self.agent_ref = agent_ref

    def send(self):
        gpu_free = self.agent_ref.get_gpu_free_mem()
        payload = {
            "node_id": self.node_id,
            "address": self.agent_ref.address,
            "gpu_free_mem": gpu_free,
            "gpu_total_mem": self.agent_ref.total_gpu_mem,
            "running_sessions": len(self.agent_ref.session_manager.sessions),
            "queue_len": self.agent_ref.local_scheduler.queue_length(),
            "loaded_models": [self.agent_ref.model_name],
            "last_heartbeat_ts": time.time()
        }
        requests.post(f"{self.scheduler_url}/v1/node/heartbeat", json=payload)

    async def run(self):
        while True:
            self.send()
            await asyncio.sleep(3)
```

------

🧩 7. Node Agent 主程序（agent.py）

```
import asyncio
from session_manager import SessionManager
from local_scheduler import LocalScheduler
from vllm_adapter import VLLMAdapter
from heartbeat import Heartbeat


class NodeAgent:
    def __init__(self, node_id, address, model_path, scheduler_url):
        self.node_id = node_id
        self.address = address
        self.model_name = model_path

        self.session_manager = SessionManager()
        self.vllm = VLLMAdapter(model_path)
        self.local_scheduler = LocalScheduler(self.vllm)

        self.heartbeat = Heartbeat(scheduler_url, node_id, self)

    def get_gpu_free_mem(self):
        # 简化：实际应读取 NVML
        return 16000

    def start(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.local_scheduler.run())
        loop.create_task(self.heartbeat.run())
        loop.run_forever()
```

------

🧩 8. Node Agent API（api.py）

用于接收 LangChain Wrapper 的推理请求。

```
from fastapi import FastAPI
from models import InferenceRequest
from agent import agent_instance   # NodeAgent singleton

app = FastAPI()


@app.post("/v1/chat/completions")
async def chat(req: InferenceRequest):
    session = agent_instance.session_manager.ensure_session(req.session_id, req.model)
    await agent_instance.local_scheduler.submit(session, req.dict())

    # 等待推理完成（简化实现）
    while not getattr(session, "last_output", None):
        await asyncio.sleep(0.005)

    return {"output": session.last_output}
```

------

🧩 Node Agent 单节点部署：

```
# 启动 Node Agent
agent_instance = NodeAgent(
    node_id="node-1",
    address="http://127.0.0.1:5001",
    model_path="gpt-4o-mini",
    scheduler_url="http://scheduler:9000"
)
agent_instance.start()
```

------

#### 8、各模块协同工作的全过程

整时序图（LangChain → Global Scheduler → Node Agent）：

```
        ┌────────────────────────┐
        │      Client / App      │
        └────────────┬──────────┘
                     │ ① 请求
                     ▼
        ┌────────────────────────┐
        │     LangChain Wrapper  │
        └────────────┬──────────┘
                     │ ② 请求 session 放置
                     ▼
        ┌────────────────────────┐
        │    Global Scheduler    │
        │  (session 放置 / 选节点 ) │
        └────────────┬──────────┘
                     │ ③ 返回 session → node 映射
                     ▼
        ┌────────────────────────┐
        │   LangChain Wrapper    │
        └────────────┬──────────┘
                     │ ④ 直接打到目标 node
                     ▼
        ┌────────────────────────┐
        │       Node Agent       │
        │  (session + batch 推理)│
        └────────────┬──────────┘
                     │ ⑤ 请求入队 (Local Scheduler)
                     ▼
        ┌────────────────────────┐
        │    Local Scheduler     │
        │ (优先级队列 + microbatch) │
        └────────────┬──────────┘
                     │ ⑥ batch 收集
                     ▼
        ┌────────────────────────┐
        │       vLLM Engine      │
        │  (真正做推理的 GPU 模型)│
        └────────────┬──────────┘
                     │ ⑦ 推理输出
                     ▼
        ┌────────────────────────┐
        │       Node Agent       │
        └────────────┬──────────┘
                     │ ⑧ 返回结果
                     ▼
        ┌────────────────────────┐
        │  LangChain Wrapper     │
        └────────────┬──────────┘
                     │ ⑨ 返回 client
                     ▼
        ┌────────────────────────┐
        │      Client / App      │
        └────────────────────────┘

```

------

简要版：

- 调度器负责全局分配
- Node Agent 负责本地批处理、高效推理
- vLLM 负责高速 GPU batch 推理

```
调度器决定 session 给哪个节点
↓
Node Agent 收到请求
↓
Session Manager 管 session
↓
Local Scheduler 把多个 session 合成 batch
↓
vLLM 做批量推理
↓
Node Agent 返回结果给 LangChain
↓
LangChain 返回给 Client
```

具体而言：

------

① LangChain Wrapper 调用调度服务创建 Session：LangChain Wrapper 负责统一代理所有模型调用

```
Client → Global Scheduler:
  POST /v1/sessions/create
    { model: "gpt-4o-mini" }

Global Scheduler:
  - 查 Redis 节点资源
  - 选择 node-3
  - 保存 session → node 映射
  - 返回 { session_id, node_id: "node-3" }
```

------

② LangChain Wrapper 获取路由：LangChain Wrapper 先问调度器，“我这个 session 应该去哪台服务器推理？”

```
Client → Global Scheduler:
  GET /v1/sessions/<id>/route
→ node-3
```

------

③ LangChain Wrapper 把推理请求打到 Node-3

```
POST http://node-3/v1/chat/completions
{
  "session_id": "...",
  "model": "gpt-4o-mini",
  "stream": false,
  "messages": [ ... ]
}
```

------

④ Node Agent 的 SessionManager

Session Manager 的工作非常简单：它存储 session 的上下文和状态。

> “这个 session 我认识，还是第一次来？”
>  “把它记下来，下次继续用。”

```
session_manager.ensure_session(session_id, model)
```

如果 session 第一次到来 → 创建 session 绑定本节点。

------

⑤ LocalScheduler 将请求放入队列（按优先级）

```
queues[priority].append((session, req))
```

补充：Local Scheduler = **本地的小型调度器**（决定哪些请求合并成 batch 去跑），它维护多条队列：

```
优先级1队列: [S1, S4, S9]
优先级2队列: [S3, S7]
优先级5队列: [S2]
```

------

⑥ LocalScheduler 通过 batch loop 收集多个 session 请求 → 送 vLLM

```
batch = [(sessionA, promptA), (sessionB, promptB)]
outputs = vllm.run_batch(prompts)
```

补充：Local Scheduler 定期批处理（micro-batching），例如每 10ms 看一眼：

```
能不能把这 6 个 session 的 prompt 合成 1 个 batch？
能，那就送给 vLLM 推理。
```

------

⑦ vLLM 生成结果 → 写回 SessionContext

```
session.last_output = "生成内容..."
```

具体来说：vLLM 会返回一个 batch 结果，例如：

```
[S1 输出内容, S2 输出内容, S3 输出内容 ...]
```

Node Agent 根据顺序把结果放回各自的 session。

------

⑧ API 返回推理结果给 LangChain Wrapper

LangChain Wrapper 再解析为 `AIMessage` 填充组件链。

换句话说，就是LangChain 又把 response 封装成`AIMessage` 返回给 client。

------

⑨ Node Agent 每 3 秒上报 Heartbeat 给 Global Scheduler

```
POST /v1/node/heartbeat
{
  node_id: node-3,
  gpu_free_mem: ...,
  running_sessions: ...,
  queue_len: ...,
}
```

Global Scheduler 维护全局资源视图，调度器据此知道每台机器的状态。

```
GPU 空闲：15000MB
排队请求：12
活跃会话数：53
已加载模型：gpt-4o-mini
```

用于后续 session 的放置。



#### 9、性能优化要点（实践清单）

1. **最大化微批**：把等待窗口控制在 5–20ms 以兼顾吞吐和延迟
2. **模型共享 & quantization**：4/8-bit，float16；避免复制 model weights
3. **Session affinity**：尽量在同节点重用 session，避免频繁加载
4. **Prompt cache & result cache**：对重复 prompt 命中缓存
5. **零拷贝**：在 node 内使用零拷贝 buffer 传递 token / logits
6. **Avoid head-of-line blocking**：优先级化调度，低优先级在不影响高优先级下扩大 batch
7. **Backpressure**：当 queue 超阈值时返回 429 或在 ingress 做速率限制
8. **Memory safety**：监控 OOM，使用 per-model memory accounting