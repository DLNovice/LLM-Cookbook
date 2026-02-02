## 基础

**Web Server 与网关**

- Uvicorn（ASGI server, async worker）
- Gunicorn（进程管理 + Uvicorn worker）
- Nginx（反向代理、负载均衡、SSL 终端）



## 实战

任务：Nginx + Gunicorn + Uvicorn 组合，实际部署 LLM API