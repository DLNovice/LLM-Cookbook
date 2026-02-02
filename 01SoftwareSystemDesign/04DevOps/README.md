## DevOps 概念

DevOps（Development + Operations）是一组融合**软件开发（Dev）与 IT 运维（Ops）**的文化理念、实践流程与自动化工具集，核心目标是：

1. 打破传统“开发—测试—运维”之间的组织壁垒，形成跨职能协作；
2. 通过自动化与持续反馈，实现**快速、可靠、可持续**的软件交付；
3. 让“构建它的人也要负责运行它”，形成共享责任、持续改进的文化。



### 核心实践

1. **持续集成 / 持续交付（CI/CD）**
   代码变更后自动构建、测试并部署到类生产环境，保证随时可发布。
2. **基础设施即代码（IaC）**
   用代码（Terraform、Ansible 等）管理服务器、网络等基础设施，实现可重复、可审计的环境交付。
3. **自动化测试与部署**
   单元/接口/UI/性能测试全部自动化；一键或零干预部署到任意环境。
4. **监控与可观测性**
   实时采集指标、日志、链路追踪，快速发现与定位线上问题。
5. **安全左移（DevSecOps）**
   将安全扫描、依赖检查、漏洞检测嵌入 CI/CD 流程，早期发现并修复风险。



## 常用工具

| 生命周期阶段    | 常用开源/商业工具                                          | 说明                           |
| --------------- | ---------------------------------------------------------- | ------------------------------ |
| 计划 / 需求     | Jira、Trello、Azure Boards、GitHub Projects                | 敏捷看板、需求分解、迭代规划   |
| 代码 / 版本控制 | Git、GitHub、GitLab、Bitbucket                             | 分支策略、Code Review、MR/PR   |
| 持续集成        | Jenkins、GitLab CI、GitHub Actions、Azure DevOps、CircleCI | 自动编译、单元测试、质量扫描   |
| 持续交付        | Argo CD、Flux、Spinnaker、Octopus Deploy                   | 自动发布到测试/预发布/生产环境 |
| 配置管理 / IaC  | Terraform、Ansible、Pulumi、AWS CloudFormation             | 环境一致性、可重复部署         |
| 容器 / 编排     | Docker、Kubernetes、Helm、Rancher                          | 标准化交付、弹性伸缩           |
| 监控 / 日志     | Prometheus + Grafana、ELK/EFK、Jaeger、Datadog、New Relic  | 指标、日志、链路追踪三位一体   |
| 协作 / 知识     | Confluence、Slack、Microsoft Teams、Wiki                   | 文档沉淀、事件协同、ChatOps    |



参考：[8 分钟速懂所有 DevOps 工具](https://www.bilibili.com/video/BV1XjnUztEsH)

- 概述了一些常用工具

