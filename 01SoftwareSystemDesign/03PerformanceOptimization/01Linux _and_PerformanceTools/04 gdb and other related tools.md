### 简介

在代码阅读时，常说基于gdb打个堆栈看主要流程。

gdb，GNU Debugger，是 Linux 下最常用的调试器，可以单步运行、打断点、查看变量、查看调用栈等。



当你对一份大型、复杂的代码不熟悉时，直接看源代码可能很难理清“程序到底是怎么跑的”。
 这时候就可以运行程序，借助 gdb 打断点，然后用堆栈回溯来直观地看到 **程序从入口一路调用到当前点的函数路径**。
 这样就能快速理解：

- 哪些函数是主要流程
- 谁调用了谁
- 程序运行的关键链路



### 应用场景

对于各类语言：

- **C/C++**：gdb 的“原生领域”，功能最强。
  - gdb 最初是 **C 和 C++** 的调试器（因为它基于 ELF 二进制、DWARF 符号表等）。后来逐渐支持了 **Fortran、Rust 等编译成原生机器码的语言**。
  - 只要语言最终编译为 **本地可执行文件**（非虚拟机字节码），基本都能用 gdb。
- **Go**：Go 官方推荐的是 **delve (dlv)**，比 gdb 更懂 Go 的运行时（goroutine、channel 等概念）。虽然可以用 gdb，但体验差。
- **Python**：因为 Python 是解释执行的，gdb 只能调 C 层（解释器本身，比如 CPython 的源码），对 Python 业务逻辑没啥帮助。
  - 调 Python 代码一般用 `pdb`（Python Debugger）。
  - 但如果你在排查 C 扩展、嵌入式 Python，gdb 就有用，还可以加载 `libpython` 的 gdb 插件，能打印 Python 栈和对象。
- **Java / C# 等虚拟机语言**：一般不用 gdb，更多是 JVM Debugger、jdb 或 IDE 自带的调试器。



对于一个“大杂烩”系统（例如：

- C++ 做核心模块
- Go 做微服务
- Python 做脚本/调度
- Java 提供 API 网关
   ）

调试的思路通常是 **“分层选工具”**：

- **进程入口/系统级**：用 gdb、strace、perf 观察进程行为、调用栈、系统调用。
- **语言层**：
  - C/C++ → gdb/lldb
  - Go → delve
  - Python → pdb 或 gdb+Python 插件（调解释器）
  - Java → jdb 或 IDE Remote Debug
- **跨进程/分布式**：还要靠日志、trace（如 OpenTelemetry、Jaeger）来串联调用链。