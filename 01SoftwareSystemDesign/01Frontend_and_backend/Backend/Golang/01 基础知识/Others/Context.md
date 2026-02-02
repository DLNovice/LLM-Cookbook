> 总结：context 用于取消、超时、链路元信息传递，按需创建，及时 cancel；每个 goroutine 必须监听 ctx.Done() 以防泄漏。

TODO：

- [面试官最爱问的Go上下文｜深入理解 Go Context 并发编程：代码实践、源码精读，设计哲学](https://www.bilibili.com/video/BV1u1YxzWEcN)



下面系统、深入地讲解 **Golang 中 context 的核心技巧、最佳实践、踩坑点及高级用法**。这不是简单 API 介绍，而是总结工程中真正实用的技巧。

------

### ✅ 1. context 的核心原则（必须牢记）

Go 官方对 context 的两个重要原则：

**1.1 Context 只用于控制取消/超时、携带请求范围的元数据**

不要用它当万能参数。

**1.2 Context 必须是函数的第一个参数**

```
func DoSomething(ctx context.Context, ...) { ... }
```

**1.3 不要把 Context 存为 struct 字段**

Context 代表请求生命周期，被存起来会导致滥用或泄漏。

------

### ✅ 2. context 的四大典型用途（工程级别）

#### **2.1 取消控制（Cancel Propagation）**

非常适合级联任务：

```
ctx, cancel := context.WithCancel(context.Background())
defer cancel()

go func() {
    select {
    case <-ctx.Done():
        fmt.Println("goroutine exit")
    }
}()
```

技巧

- 多层 goroutine 自动共享取消信号。
- 父协程 cancel，所有子协程同步退出（防泄漏）。

------

#### **2.2 超时控制（Timeout & Deadline）**

避免 goroutine 永远挂住。

```
ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
defer cancel()
```

技巧

- 比 waitgroup 更适合有超时需求的场景。
- deadline 适合系统级统一超时，如 HTTP server。

------

#### **2.3 元数据传递（Value）**

少用，但用于：

- request_id
- 用户信息
- trace_id

```
ctx = context.WithValue(ctx, UserIDKey, 10086)
```

注意（非常容易踩坑）

❌ 不要传递大对象、业务数据、配置、实体对象
 ❌ 不要滥用 value，它不是 `map[string]interface{}`

------

#### **2.4 控制外部资源（DB、HTTP、gRPC、Redis）**

例如 GMysql：

```
rows, err := db.QueryContext(ctx, "SELECT ...")
```

信号级联会使 DB driver 主动停止 IO。

------

### ✅ 3. 常用 Context 模式（实际工程技巧）

------

#### 🔥 **3.1 结构化并发（Go1.21 sync.ErrGroup 源于此思想）**

推荐使用 `errgroup.WithContext`：

```
g, ctx := errgroup.WithContext(context.Background())

for i := 0; i < 3; i++ {
    g.Go(func() error {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
            // do work
        }
        return nil
    })
}

if err := g.Wait(); err != nil {
    log.Println("exit:", err)
}
```

好处

- 任意一个 goroutine 错误 → 自动取消全部任务
- 无需手写 wait group + cancel 组合

------

#### 🔥 **3.2 防止 goroutine 泄漏的 always-listen 技巧**

```
func worker(ctx context.Context, ch <-chan int) {
    for {
        select {
        case <-ctx.Done():
            return
        case v := <-ch:
            fmt.Println(v)
        }
    }
}
```

核心技巧

**每个 goroutine 都必须监听 ctx.Done()**
 这是避免 goroutine 泄漏的最佳方式。

------

#### 🔥 **3.3 在 HTTP 服务中传递 request-scope 数据**

```
func handler(w http.ResponseWriter, r *http.Request) {
    ctx := context.WithValue(r.Context(), RequestID, uuid.New())
    process(ctx)
}
```

#### 注意

要用 `r.Context()` 而不是 `context.Background()`
 否则失去 HTTP 取消和超时特性。

------

#### 🔥 **3.4 禁止 context 存在孤儿超时（leak timeout）**

错误：

```
func A(ctx context.Context) {
    ctx2, _ := context.WithTimeout(ctx, 1*time.Second) // cancel 丢了
}
```

正确：

```
ctx2, cancel := context.WithTimeout(ctx, 1*time.Second)
defer cancel()
```

**即使你提前 return，cancel 必须调用**

------

#### 🔥 **3.5 context 在 channel/select 中的经典模式**

```
select {
case <-ctx.Done():
    return ctx.Err()
case msg := <-ch:
    ...
}
```

技巧

将 context 作为选项之一，可以优雅终止阻塞的 channel 接收。

------

#### 🔥 **3.6 防止 panic：Value key 必须是独立类型**

错误：

```
ctx = context.WithValue(ctx, "uid", 1) // 字符串不可控
```

正确：

```
type ctxKey string
const UserIDKey ctxKey = "uid"
ctx = context.WithValue(ctx, UserIDKey, 1)
```

------

#### 🔥 **3.7 与 defer cancel 的最佳时机**

- 如果等待结果的函数内部会阻塞，需要 `defer cancel()`
- 如果直接返回则不要 defer，直接 cancel（更快释放资源）

示例：

```
ctx, cancel := context.WithTimeout(ctx, 3*time.Second)
resp, err := httpClient.Do(req.WithContext(ctx))
cancel() // 不用 defer，更快释放网络连接
```

------

#### 🔥 **3.8 提前取消的技巧**

提前 cancel 能加速 GC 回收，例如大型任务分片处理时。

------

#### 🔥 **3.9 context 作为状态机信号**

例如：

```
ctx, stop := context.WithCancel(context.Background())

func StopService() {
    stop() // 让整个后台服务关闭
}
```

context 即信号量，本质是 thread-safe 的广播。

------

#### 🔥 **3.10 可组合 cancel（子系统继承父系统超时）**

```
func handler(ctx context.Context) {
    ctx2, cancel := context.WithTimeout(ctx, 500*time.Millisecond)
    defer cancel()

    processA(ctx2)
    processB(ctx2)
}
```

父超时会终止全部子任务。

------

#### 🔥 **3.11 context 层级清晰的最佳实践结构**

建议结构如下：

```
http request ctx → router → middleware → handler
→ business logic → db/cache/io
```

所有任务共享同一个 context。

------

### 🧨 4. context 常见错误（踩坑清单）

| 错误                          | 原因                         |
| ----------------------------- | ---------------------------- |
| ❌ context value 滥用          | 变成万能 map，反而导致反模式 |
| ❌ context 一路传但不监听 Done | 取消信号没意义               |
| ❌ 忘记 cancel                 | 超时 context 泄漏            |
| ❌ 把 context 存到 struct      | 生命周期混乱                 |
| ❌ 在库代码中滥用 value        | 用户无法控制 key             |