项目来源：

- B站入门项目
- Github开源项目
- [CNCF 项目](https://contribute.cncf.io/projects/)：[CNCF Landscape](https://landscape.cncf.io/)
- 某鱼买项目等



## 待归纳

### amitshekhariitbhu/go-backend-clean-architecture

> A Go (Golang) Backend Clean Architecture project with Gin, MongoDB, JWT Authentication Middleware, Test, and Docker.
>
> - Github：https://github.com/amitshekhariitbhu/go-backend-clean-architecture
> - Others：[Go项目结构最佳实践，你觉得怎么样？](https://www.bilibili.com/video/BV1sJ4m1L7RN)

22年的项目，目前接近 6kstar，核心在于提供了一个很清晰干净的Golang后端架构设计，虽然实际业务中可能不会采用此类固定项目结构，但是值得参考。

```Mermaid
flowchart TB
  %% Layers
  subgraph Delivery["Delivery / API Layer"]
    Routes["api/route/*"]
    Controllers["api/controller/*"]
    Middleware["api/middleware/*"]
  end

  subgraph Usecase["Usecase / Application Layer"]
    Usecases["usecase/*"]
  end

  subgraph Domain["Domain Layer"]
    Entities["domain/* (Entities, DTOs)"]
    Interfaces["domain/* (Interfaces)"]
  end

  subgraph Infra["Infrastructure Layer"]
    Repos["repository/*"]
    MongoAbst["mongo/* (DB Abstraction)"]
    TokenUtil["internal/tokenutil/*"]
  end

  subgraph Bootstrap["Bootstrap / Composition Root"]
    Main["cmd/main.go"]
    Boot["bootstrap/* (env, db)"]
  end

  subgraph External["External Systems"]
    Gin["Gin HTTP Server"]
    MongoDB["MongoDB"]
    JWT["JWT Library"]
  end

  %% Wiring / flow
  Main --> Boot
  Main --> Gin
  Boot --> MongoDB

  Routes --> Controllers
  Routes --> Middleware
  Controllers --> Usecases
  Usecases --> Interfaces
  Repos --> Interfaces

  %% Infra dependencies
  Repos --> MongoAbst
  MongoAbst --> MongoDB

  %% Token utility usage (not pure Clean Architecture)
  Usecases --> TokenUtil
  TokenUtil --> JWT

  %% Server entry
  Gin --> Routes

  %% Domain references
  Controllers --> Entities
  Usecases --> Entities
  Repos --> Entities
```

------

#### **0）项目源码阅读指北**

下面是对你给出的内容的**中文翻译**，保持了**教学导向、结构和语义准确性**，适合直接放进技术文档或学习笔记中。

------

**一种实用、可重复的代码阅读顺序与心智模型（适用于 Clean Architecture 项目）**

下面是一套**实践性强、可反复使用的阅读顺序与思考方式**，专门用于这类 **Clean Architecture 风格** 的项目。
它的目标是：**先理解设计意图，再用代码验证细节**。

------

**阅读策略（顺序 + 目的）**

**1、入口点 & 组合根（Composition Root）**

从应用是如何启动、如何完成依赖组装开始。

- `cmd/main.go`
- `bootstrap/*`

**目标：**

- 理解应用运行时是如何被组装的
- 明确外部系统（配置、数据库、HTTP 框架）从哪里进入系统

------

**2、Routes → Controllers（交付层请求流）**

查看请求是如何进入系统、如何被映射和处理的。

- `api/route/*`
- `api/controller/*`

**目标：**

- 识别系统对外暴露了哪些接口（Endpoints）
- 理解请求 / 响应的整体模式

------

**3、Usecases（核心业务编排层）**

深入“业务逻辑”的核心层。

- `usecase/*`

**目标：**

- 观察业务流程是如何被组织的
- 搞清楚 usecase 依赖了哪些接口（而不是具体实现）

------

**4、Domain（契约与实体）**

阅读领域模型和接口定义。

- `domain/*`

**目标：**

- 理清核心实体（Entities）
- 理解 DTO（请求 / 响应结构）
- 明确 repository / usecase 的接口契约

------

**5、基础设施与持久化实现**

查看接口的具体实现方式。

- `repository/*`
- `mongo/*`

**目标：**

- 理解数据访问是如何被抽象的
- 明白测试是如何在不依赖真实数据库的情况下进行的

------

**6、横切关注点（Cross-cutting Utilities）**

安全、Token、内部工具等。

- `internal/*`

**目标：**

- 识别哪些地方使用了具体实现
- 发现 usecase 与基础设施耦合的“泄漏点”

------

**每一步需要重点关注的内容**

- **依赖方向**
  - 谁依赖谁？依赖是否指向领域层？
- **边界对象**
  - DTO vs Entity vs Model 的职责划分
- **转换发生的位置**
  - 是在 controller？usecase？还是 repository？
- **组合根（Composition Root）在哪里**
  - 依赖是在哪里被创建和注入的？
- **可测试切入点**
  - 接口、mock、context timeout 等

------

**一个聚焦的学习路径（强烈推荐）**

1. 先阅读 **README**，了解作者期望的架构设计
2. 选择 **一个接口**（例如 `/task`），从头到尾完整追踪一次
3. 将总结出的模式推广到其他接口
4. 最后深入一个基础设施模块（Mongo / JWT），理解抽象的实现方式

------

**为什么这种顺序有效**

- 你会 **先理解“为什么这样设计”**
- 再深入 **“具体是怎么实现的”**
- 能更早看清 **架构约束**（接口、依赖注入、边界）

------

#### **1）整体架构风格（宏观视角）**

该项目采用的是一种**受 Clean Architecture 启发的分层架构设计**：

- **入口 / 交付层（Entry / Delivery）：**
  `api/route`, `api/controller`, `api/middleware`
- **用例层（Usecase / Application）：**
  `usecase/`
- **领域层（Domain）：**
  `domain/`（实体、请求/响应 DTO、接口）
- **基础设施层（Infrastructure）：**
  `repository/`, `mongo/`, `internal/`
- **启动 / 组合根（Bootstrap / Composition Root）：**
  `cmd/`, `bootstrap/`

**职责与边界**

- **Domain（领域层）**
  - 定义核心实体和接口（如 `TaskRepository`、`TaskUsecase`、`UserRepository`）
  - 定义请求 / 响应结构体
- **Usecase（用例层）**
  - 实现应用层的业务流程
  - 只依赖 domain 中定义的接口
- **Repository（仓储层）**
  - 实现 domain 中的仓储接口
  - 通过 `mongo` 抽象与 MongoDB 通信
- **Controller（控制器）**
  - 处理 HTTP 相关逻辑（Gin 参数绑定、鉴权头、HTTP 状态码）
- **Route（路由层）**
  - 负责依赖注入（controller + usecase + repository）
  - 绑定 HTTP 路由
- **Bootstrap**
  - 创建环境配置和数据库客户端

**依赖方向**

- 依赖始终**向内指向**
  （controller → usecase → domain；repository → domain）
- 基础设施层依赖 domain 定义的接口

**一个值得注意的偏离点：**

- `usecase/signup_usecase.go` 直接调用了 `internal/tokenutil`
- 这是一个**实用上的捷径**，但并非“纯粹”的 Clean Architecture
  （usecase 依赖了具体实现，而不是接口）

------

#### **2）目录结构 & 为什么要这样拆分**

**核心、关键部分**

`domain/`

- **核心内容**
  - 实体模型（`User`, `Task`）
  - 请求 / 响应 DTO（`SignupRequest`, `SignupResponse`）
  - 接口定义
- **为什么单独拆分？**
  - 保持业务核心和契约稳定
  - 其他层都可以安全依赖它

`usecase/`

- **核心内容**
  - 应用层业务逻辑与流程编排（如注册、创建任务）
- **为什么单独拆分？**
  - 隔离业务规则
  - 避免 HTTP / DB 逻辑渗透进业务逻辑

`api/`

- **核心入口**
  - 路由注册
  - 请求解析
  - 响应处理
- **为什么单独拆分？**
  - 方便替换 HTTP 框架
  - 或同时支持多种入口（HTTP / gRPC 等）

------

**支撑 / 基础设施 / 教学演示部分**

`repository/`

- **职责**
  - 数据访问层的具体实现
  - 通过 `mongo/` 使用 MongoDB
- **为什么单独拆分？**
  - 便于 mock
  - 切换数据库时不影响 usecase

`mongo/`

- **职责**
  - 对官方 Mongo Driver 的抽象（`Database`、`Collection` 等接口）
- **为什么单独拆分？**
  - 让 repository 在测试中不依赖真实 MongoDB

`bootstrap/`, `cmd/`

- **职责**
  - 应用启动
  - 依赖组合
  - `cmd/main.go` 是真正的入口
- **为什么单独拆分？**
  - 明确组合根（Composition Root）
  - 保持主入口干净

`internal/`

- **职责**
  - JWT Token 的生成与校验工具
- **为什么单独拆分？**
  - 防止被外部包直接引用
  - 但也导致 usecase 依赖具体实现

------

**初学者容易困惑的点**

- **`domain/` 中包含 DTO**
  - 如 `SignupRequest` 和实体混在一起
- **`repository/` 并不是“领域仓储”**
  - 而是领域仓储接口的**具体数据库实现**
- **`mongo/` 抽象**
  - 对学习阶段来说可能显得“多此一举”
  - 实际目的是可测试性和可替换性

------

#### **3）核心数据流（示例：创建 Task 接口）**

选择 **私有 `/task` POST** 接口，因为它包含 middleware + usecase + repository 的完整流程。

**文本时序图**

```
Client -> Gin Router -> JWT Middleware -> TaskController -> TaskUsecase -> TaskRepository -> MongoDB
```

------

**逐步流程**

1. **请求进入**
   - `api/route/task_route.go`
   - Gin 路由 `/task`
2. **JWT 中间件**
   - `api/middleware/jwt_auth_middleware.go`
   - 校验 Token
   - 将 `x-user-id` 写入 Gin context
3. **Controller**
   - `api/controller/task_controller.go`
   - 将表单数据绑定到 `domain.Task`
   - 从 context 读取 `x-user-id` 并转为 `ObjectID`
   - 调用 `TaskUsecase.Create`
4. **Usecase**
   - `usecase/task_usecase.go`
   - 创建 `context.WithTimeout`
   - 调用 `TaskRepository.Create`
5. **Repository**
   - `repository/task_repository.go`
   - 通过 `mongo.Database` 写入 MongoDB
6. **Controller 返回响应**

------

**DTO / 实体的使用方式**

- `domain.Task` 同时承担：
  - **请求 DTO**（`form:"title"`）
  - **数据库实体**（`bson` tag）
- 没有单独的 DTO 层
- Domain 结构体被多角色复用

**为什么要在 Controller 中做转换？**

- 将 HTTP 相关细节限制在 Controller
- 保证 Usecase 不感知 HTTP

------

#### **4）值得学习的设计亮点（3–5 点）**

1. **清晰的分层，最小化跨层认知**
   - Controller 不接触 Mongo
   - Repository 不关心 HTTP
2. **通过 Domain 接口实现依赖反转**
   - Usecase 依赖接口，易于 mock 测试
3. **路由层即组合根**
   - 集中完成依赖注入
4. **`mongo/` 基础设施抽象**
   - 提升可测试性
5. **Usecase 中统一的 Context 超时控制**
   - 超时策略集中、清晰

**教学导向 vs 生产导向**

- 对教学和测试：
  - `mongo/` 抽象和严格分层非常优秀
- 对小型生产服务：
  - 这种层级和间接性可能显得偏重

------

#### **5）权衡与潜在问题**

**成本**

- **学习曲线高**
  - 需要理解多层结构和接口
- **代码开销大**
  - 简单逻辑也需要多个文件

**不太适合的场景**

- 小型 MVP
- 快速验证阶段
- 团队不熟悉 Clean Architecture

**可以简化的地方**

- 小项目中合并 `mongo/` 和 `repository/`
- 只有当领域模型复杂时再引入专用 DTO
- 极简单 CRUD 服务中合并 usecase + repository

------

**架构纯度说明**

- Usecase 直接依赖 `internal/tokenutil`
- 在“纯” Clean Architecture 中：
  - Token 生成应定义在 domain 接口中
  - 由 infra 层提供实现

------

#### **6）可迁移的实践 & 演进路径**

**强烈建议保留**

- **Domain 中定义接口**
- **Usecase 层作为业务编排中心**
- **明确的组合根（Composition Root）**
- **Usecase 中的 Context 超时控制**

**可逐步引入**

- 当测试或数据库替换有需求时再引入 `mongo/`
- 当 API 与领域模型明显分化时再拆 DTO

------

**推荐的演进路径**

**小型项目（1–2 人）**

- `cmd/`, `api/`, `domain/`, `repository/`
- 可合并 usecase 与 repository
- 接口最小化

**中型项目（3–8 人）**

- 完整 `domain/` + `usecase/` + `repository/`
- 保留 `api/` + `bootstrap/`
- 引入 mock 测试

**复杂项目（大型团队 / 多服务）**

- 完整 Clean Architecture
- 各入口层独立 DTO
- Token / Auth / Cache / Queue 等全部接口化
- 更强的领域隔离与测试体系

------

