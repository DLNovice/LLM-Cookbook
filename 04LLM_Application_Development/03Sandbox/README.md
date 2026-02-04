> 沙箱环境可以具化为：浏览器沙箱环境、代码执行沙箱环境、终端沙箱环境、文件沙箱环境等

### 概述

以下是查到的一些沙箱环境项目（需不定期更新）：

- 阿里： AgentRun 平台，参考
  - [快速上手：LangChain + AgentRun 浏览器沙箱极简集成指南](https://mp.weixin.qq.com/s/2LjN6LxymuZNlWUR-nhrEg)
  - [进阶指南：BrowserUse + AgentRun Sandbox 最佳实践](https://mp.weixin.qq.com/s/R_I-Bgx8_UhymuMm93LUoQ)
  - [AgentRun Sandbox SDK 正式开源！集成 LangChain 等主流框架](https://mp.weixin.qq.com/s/DVeUIeCxdUJW5NuWGP0bNw)
- [docker官方](https://docs.docker.com/ai/sandboxes)：还在实验中，未出正式版
- [kubernetes-sigs/agent-sandbox](https://github.com/kubernetes-sigs/agent-sandbox)：202601 - 650 star，对K8s与云原生生态支持良好
- [agent-infra/sandbox](https://github.com/agent-infra/sandbox)：
  - 202601 - 2k star，AIO Sandbox is an all-in-one agent sandbox environment that combines Browser, Shell, File, MCP operations, and VSCode Server in a single Docker container. 
  - [为 AI Agent 打造的一体化、可定制的沙箱环境](https://mp.weixin.qq.com/s/RViNIpYYW_-q1WLsAsO-eQ)
- LangChain：
  - [LangChain - 2025.11.13 Execute Code with Sandboxes for DeepAgents](https://www.blog.langchain.com/execute-code-with-sandboxes-for-deepagents/)：We currently support sandboxes from 3 of our partners: [Runloop](https://www.runloop.ai/?ref=blog.langchain.com), [Daytona](https://www.daytona.io/?ref=blog.langchain.com), and [Modal](https://modal.com/?ref=blog.langchain.com).
- [E2B](https://github.com/e2b-dev/E2B)：
  - 202601 - 10k star，[E2B](https://www.e2b.dev/) is an open-source infrastructure that allows you to run AI-generated code in secure isolated sandboxes in the cloud. To start and control sandboxes, use our [JavaScript SDK](https://www.npmjs.com/package/@e2b/code-interpreter) or [Python SDK](https://pypi.org/project/e2b_code_interpreter).
- [daytona](https://github.com/daytonaio/daytona)：
  - 202601 - 46k star，Run AI Code. Secure and Elastic Infrastructure for Running Your AI-Generated Code.
  - [基于 LangChain Deep Agents 与 Sandbox 集成 Claude Skills 的智能体开发指南](https://mp.weixin.qq.com/s/lEtawBwHqu-AMARvvNadHQ)




> 参考：[请别占用我的电脑！Agent 运行背后的秘密](https://www.bilibili.com/video/BV1iTmQBxEbT)

常用虚拟化技术：

- 虚拟机（隔离）：VMware
- 容器（轻量）：Docker
- 微型虚拟机（兼顾）：Firecracker

国产：腾讯云沙箱、E2B、AgentCore等

ChatGPT：第一次运行时直接给浏览器下载一个Python解释器

开源项目：略

利用快照/预热，快速完成项目初始化，而非从0加载
