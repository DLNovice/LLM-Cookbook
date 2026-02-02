## 01 Linux 与性能分析工具（基础）

**环境与基础**

- Linux 进程/线程/内存模型
- I/O 模型（阻塞/非阻塞/epoll）

**常用工具**

- `top`, `htop`, `iotop`, `dstat`（系统级监控）
- `strace`（系统调用追踪）
- `perf`（CPU 性能采样与热点分析）
- `gdb`（调试、死锁/崩溃分析）
- `valgrind`（内存泄漏、内存越界检测）
- `nsight`, `vtune`（GPU & CPU 高级分析，LLM 推理优化必学）

备注：上述多数功能偏向C++高频性能调优相关（例如：[C++面试高频性能调优全流程：gprof、perf、valgrind、kcachegrind 全解](https://www.bilibili.com/video/BV1W9Nzz7EXS)）



## 02 性能问题定位与优化（进阶）

**内存相关**

- 内存泄漏排查（valgrind, heaptrack）
- Python 内存管理 & GC 分析（objgraph, tracemalloc）

**CPU/IO 瓶颈**

- 多线程 vs 多进程
- 异步 IO & 协程调度（asyncio, uvloop）
- 事件驱动模型（Reactor, Proactor）

**典型优化手段**

- 缓存（Redis, 本地 LRU 缓存）
- 批量请求/批量推理（Batching）
- 模型量化与并行推理优化



## 03 高并发部署与网关（应用层）

**Web Server 与网关**

- Uvicorn（ASGI server, async worker）
- Gunicorn（进程管理 + Uvicorn worker）
- Nginx（反向代理、负载均衡、SSL 终端）

**部署模式与调优**

- Gunicorn worker 类型选择（sync, async, uvicorn-worker）
- 并发连接数、超时、连接池优化
- Nginx 缓存、限流、健康检查



任务：Nginx + Gunicorn + Uvicorn 组合，实际部署 LLM API



## 04 服务网格与可观测性（体系化能力）

**服务网格概念**

- Sidecar 模式（Envoy）
- 控制面 & 数据面

**常见框架**

- Istio（全功能，企业常用）
- Linkerd（轻量级，简单场景）

**关键功能**

- 流量管理（蓝绿部署、灰度发布、A/B 测试）
- 可观测性（tracing, metrics, logging）
- 安全性（mTLS, service-to-service auth）