## 手搓简易Agent

> 参考：
>
> - 视频教程：[【手搓代码】咱们一起从零开始构建大模型智能体第1集](https://www.bilibili.com/video/BV1zJLUzZE2P)
> - 项目地址：https://github.com/TongTong313/LLM-TT

Agent底层采用openai api（ChatCompletionMessage），具备基础的工具调用能力和短期记忆能力，可以学习其源码。



### 主函数分析

参考：

```python
from mymanus.prompt import SYSTEM_PROMPT as system_prompt
from mymanus.agent import ToolCallingAgent, ToolManager, MemoryManager, LLM
from mymanus.tool import *
import os
from loguru import logger
import asyncio
import traceback

MAX_STEP = 5


async def main():
    # 初始化大模型
    api_key = os.getenv("DASHSCOPE_API_KEY")
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # 初始化大模型->智能体的大脑
    llm = LLM(api_key=api_key,
              base_url=base_url,
              model="qwen-plus-latest",
              max_tokens=8000,
              tool_choice="auto",
              stream=True,
              enable_thinking=False)

    # 初始化工具管理器
    tool_manager = ToolManager()
    # 初始化记忆管理器
    memory_manager = MemoryManager(max_memory=20)
    # 初始化智能体
    agent = ToolCallingAgent(llm=llm,
                             tool_manager=tool_manager,
                             memory_manager=memory_manager,
                             max_step=MAX_STEP)

    # 注册工具
    agent.add_tool(baidu_search, tool_name="baidu_search")
    agent.add_tool(get_current_time, tool_name="get_current_time")
    agent.add_tool(terminate, tool_name="terminate")
    agent.add_tool(add, tool_name="add")

    while True:
        try:
            prompt_list = [{"role": "system", "content": system_prompt}]
            prompt = input(
                "我是童发发开发的manus超级助手，请输入你的需求，我会尽力解决你的问题，输入quit/exit可退出：")
            if prompt.lower() in ["quit", "exit"]:
                logger.warning("再见!")
                break

            # 要把prompt变为字典送入
            prompt_dict = [{"role": "user", "content": prompt}]
            prompt_list.extend(prompt_dict)

            # 运行智能体
            logger.warning(f"智能体正在运行中……")
            result = await agent.run(prompt_list)

            if result:
                logger.warning(f"智能体执行完成")
        except KeyboardInterrupt:
            logger.warning("再见!")
            break
        except Exception as e:
            logger.error(f"智能体运行错误: {e}")
            logger.error("错误堆栈信息:")
            logger.error(traceback.format_exc())
            break


if __name__ == "__main__":
    asyncio.run(main())
```

主函数写的非常直观，初始化模型类、工具类、记忆类，开始循环对话。

```python
main.py
├── 配置常量（MAX_STEP）
├── async main()
│   ├── 初始化 LLM
│   ├── 初始化 ToolManager
│   ├── 初始化 MemoryManager
│   ├── 初始化 Agent（依赖注入）
│   ├── 注册工具
│   └── 交互循环（Human ↔ Agent）
└── asyncio.run(main())
```



### LLM类实现

源码解析（`src/mymanus/agent/llm.py`）：LLM类是如何实现的？

1）`def __init__`：为什么LLM类中要定义这些参数，因为这是openai定义的接口规范，也是最小但完整的 Agent LLM 配置集。

2）`async def chat`

- 参数比较好理解，都是聊天（client.chat.completions）所需的参数
  - request_params的构造方法符合工业级写法，OpenAI Chat API 是声明式 API（现代化Python比较推崇，可读性更高、解耦等），不是对象 API
- 对流式、非流式分别做处理，特别是工具部分
  - 注意如何拼接流式返回值，特别是tool_calls部分（比较少见）

------

源码解析（`src/mymanus/agent/agent.py`）：

1）`class BaseAgent(BaseModel)`

- 为什么继承 Pydantic：明确 Agent 是一个 状态对象、自动校验依赖是否齐全、方便未来序列化 / 配置化，这是 Pydantic + Agent 的标准姿势
- 为什么 `BaseAgent.run()` 是抽象的？未来可能有PlannerAgent、MultiAgent等多种Agent，这是 模板方法模式（Template Pattern），没必要在这里就写死Agent

2）`class ToolCallingAgent(BaseAgent)`：简单且完整的Agent基座，具备ReAct、Tool Calling、Memory、多轮控制，这就是 OpenAI 官方 Agent 的最小实现形态。

- `async def think`：标准 ReAct 的 THINK 阶段

  ```python
  async def think(self, message: List[Dict]) -> bool:
          """使用大模型进行思考，返回是否需要使用工具
          
          Args:
              message (List[Dict]): 消息列表
  
          Returns:
              bool: 是否需要使用工具
          """
          # 添加终止提示
          message.append({"role": "user", "content": self.next_step_prompt})
          response = await self.llm.chat(
              messages=message, tools=self.tool_manager.get_tool_schema_list())
  
          # 回复内容全部加入记忆模块，加入的得是字典
          self.memory_manager.add_message(response.model_dump())
          # 打印回复内容，流式输出会自动打印，不必要重复打印
          if response.content and not self.llm.stream:
              logger.info(f"智能体回复：{response.content}")
          # 判断是否需要使用工具
          if response.tool_calls:
              return True
          else:
              return False
  ```

  - 关键点 1：追加 NEXT_STEP_PROMPT `message.append({"role": "user", "content": self.next_step_prompt})`，这是强制模型进入规划模式，没有这一步，模型会直接聊天，不会规划。
  - 关键点 2：tools 永远传 `tools=self.tool_manager.get_tool_schema_list()`，这是 OpenAI 的硬规则（如果中途有一次调用没带 tools，模型会“失忆”）

- `async def act`：三件事

  - 按顺序执行多个工具 `for tool_call in message["tool_calls"]`，符合 OpenAI 多工具并发设计。
  - tool result 以 role=tool 返回 `tool_message = {"role": "tool","content": tool_result,"tool_call_id": tool_id,}`
  - terminate 不是 magic，是普通工具。`if tool_name == "terminate":`这是非常成熟的 Agent 设计思想，Agent 的停止权 = 工具的一部分，而不是（新手常犯）：`if "完成" in response.content`

-  `run_step()` ：

  - ReAct 原子循环。`THINK → ACT → 判断是否终止`

- `run()`：Agent 生命周期控制器



### 记忆管理

仅有50多行，即可实现短期记忆管理

- 初始化：存储memory的列表
  - 基于Pydantic类实现数据类型实体化验证，在工程项目中非常常用
  - 为什么用 Pydantic？不是为了 fancy，而是：强类型边界、未来可以load / dump 以及配置化、和 `BaseAgent` 体系保持一致
  - 细节：使用Field时，用default还是default_factory？
- 方法：对记忆，实现增加、获取、清空



### 工具管理

参考`src/mymanus/agent/tool_manager.py`：

`class BaseTool(BaseModel, ABC)`：

- 继承BaseModel，定义抽象类

- 为什么 BaseTool 不是直接 FunctionTool？因为在为未来留接口，这是框架级思维，不是 demo。

  ```python
  BaseTool
   ├── FunctionTool（Python 函数）
   ├── APITool（HTTP API）
   ├── MCPTool（远程）
   ├── SQLTool
  ```

- `@model_validator(mode="after")`：这是一个高分设计，1）工具注册时允许最小输入；2）tool_name / description / schema 可自动推导；3）避免 register_tool 时写一堆重复信息。

  ```python
  @model_validator(mode="after")
  def initialize_tool_info(self) -> "BaseTool":
      """有一些参数是None，通过model_validator机制把默认信息填进去，初始化工具相关的属性"""
      if self.tool_name is None:
          self.tool_name = self._get_tool_name()
      if self.tool_description is None:
          self.tool_description = self._get_tool_description()
      if self.tool_schema is None:
          self.tool_schema = self._get_tool_schema()
      return self
  ```

备注：

- `@abstractmethod` 是给写代码的人看的规则：它强制子类必须实现某个方法（立规矩）。
- `@model_validator` 是给运行的数据看的规则：它在数据加载完成后进行逻辑检查（把关卡）。

------

`class FunctionTool(BaseTool)`：继承BaseTool，重写类方法。 

- 为什么 FunctionTool 要干这么多事？LLM 不认识 Python，LLM 只认识 JSON Schema
- `def _get_tool_name`：获取工具名称
- `def _get_tool_description`：按照不同注释风格，Google和Numpy风格，都能提取tool_description。大多数项目只支持一种，这里是生产级考虑支持三种
- `def _get_tool_schema`：在 docstring 里写的 schema 和 OpenAI 文档一字不差，已经是 严谨级 Tool Schema 了

针对`def _get_param_type_for_tool_schema`：转换为大模型认识的格式（tool schema），源代码注释写的很详细，可仔细阅读。

```python
def _get_param_type_for_tool_schema(self,
                                        type_hint: Type) -> Dict[str, Any]:
        """获取参数类型，并转换为openai工具schema兼容的类型，考虑到部分非标准化编程的情况
        这个函数能用，但绝对没有涵盖所有情况^_^
        
        Args:
            type_hint (Type): 由get_type_hints函数获取的参数的【类型】，兼容python源生类型和typing类

        Returns:
            (Dict[str, Any]): 参数类型schema
            例如：
            {
                "type": "array",
                "items": {
                    "type": "integer"
                }
            }
        """
        # 首先必须要搞清楚get_origin函数和get_args函数的作用
        # get_origin函数：获取给予typing类的类型提示的python原始类型（如list、dict、tuple等），但如果类型提示是python内置类型或者其他玩意，则返回None。此外，无论这个类型被嵌套了多少层，get_origin函数都仅返回最外层的类型，如List[List[List[int]]]，get_origin函数仅返回list
        # get_args函数：如果出现类型嵌套，就返回嵌套的全部类型，如果没嵌套，就返回空tuple。例如List[List[List[int]]]，get_args函数返回(typing.List[typing.List[int]],)；Dict[str, List[int]]，get_args函数返回(<class 'str'>, typing.List[int])。对于Literal[a, b, c]，get_args函数返回(a, b, c)

        # 思路：结合ori_type和args_type来处理参数类型，因为各种嵌套咱们无法估计，所以采用递归是一个好办法，既然采用递归，那我们实际上只用考虑最简单的情况即可，把原子化能力解决完，剩下的就是递归调用自己

        # 接下来我们就用get_origin和get_args来
        ori_type = get_origin(type_hint)
        args_type = get_args(type_hint)

        if ori_type in [list, tuple] or type_hint in [
                list, tuple
        ]:  # 处理List、List[T]、Tuple、Tuple[T]，T代表任意类型（递归调用不用管T到底是什么）
            # 判断有没有嵌套
            # List和Tuple的嵌套只会有一个参数，比如List[str]或List[List[str]]，而不可能是List[str, int]，所以args_type = (T,)，args_type[0]就能取到元素的类型
            # List是和Tuple需要一个额外的items字段表明每个元素的类型
            item_type = args_type[0] if args_type else None
            if item_type:  # 有type就加，没有type就不加这个items就好了
                return {
                    "type": "array",
                    "items": self._get_param_type_for_tool_schema(
                        item_type)  # 递归调用，万一又是一个List
                }
            else:
                return {"type": "array"}
        elif ori_type == dict or type_hint == dict:  # 处理Dict或Dict[K, V]这种情况
            # 同样判断有没有嵌套，K不太可能嵌套，但V还可能嵌套，比如Dict[str, List[int]]
            # 这里args_type = (K, V)，args_type[0]取到K的类型，args_type[1]取到V的类型，我们只需要分析V的类型
            value_type = args_type[1] if args_type else None
            if value_type:
                return {
                    "type":
                    "object",
                    "additionalProperties":
                    self._get_param_type_for_tool_schema(value_type)
                }
            else:
                return {"type": "object"}
        elif ori_type == Literal:  # 处理Literal[a, b, c]这种情况，a、b、c同种类型
            # 这里特殊，a、b、c直接放到enum字段里就可以
            # 获得a、b、c的类型，注意_get_param_type_for_tool_schema函数返回的是一个字典，字典的type字段才是类型
            literal_type = self._get_param_type_for_tool_schema(
                type(args_type[0]))["type"]
            return {
                "type": literal_type,
                "enum": list(args_type) if args_type else []
            }
        elif ori_type == Union:  # 处理Union或者Optional情况
            # 用anyOf来处理，把所有可能的类型都列出来
            return {
                "anyOf": [
                    self._get_param_type_for_tool_schema(arg)
                    for arg in args_type
                ]
            }

        # 到目前为止，ori_type生成typing类型的情况就处理完了，那其他情况大概率返回就是None了，我们无法从ori_type获取信息，只能从type_hint获取信息了
        # 为啥没有list和dict？
        if type_hint == int:
            return {"type": "integer"}
        elif type_hint == float:
            return {"type": "number"}
        elif type_hint == bool:
            return {"type": "boolean"}
        elif type_hint == type(None):
            return {"type": "null"}
        elif type_hint == str:
            return {"type": "string"}
        elif type_hint == list:
            return {"type": "array"}

        return {"type": "string"}  # 保底！
```

解析：

- 为什么必须这么写：OpenAI tools schema 支持type、items、enum、anyOf、object，而 Python typing 有List、Dict、Optional、Union、Literal、嵌套，这本质上是一个“类型系统翻译器”。
- 用 get_origin / get_args：很多人完全不知道这两个函数是干嘛的，具体解释间上述代码
- 用递归解决嵌套问题：`return self._get_param_type_for_tool_schema(item_type)`
- Literal → enum（完全符合 OpenAI 规范）、Union / Optional → anyOf

------

`class ToolManager`：工具管理类，管理所有的工具。符合OpenAI的要求。

| OpenAI 要求         | 你实现               |
| ------------------- | -------------------- |
| tool list           | get_tool_schema_list |
| name → function     | tools dict           |
| tool_call → execute | execute_tool         |

几个常见错误（这里没有犯）：

- 不在这里做 LLM 调用
- 不在这里做 memory
- 不混 prompt

只做 注册、执行、schema 管理，这是 Single Responsibility Principle（单一职责）。



### 补充

> 架构设计类问题

Q: 为什么 Agent 每次 `run()` 后要清空记忆？这会导致什么问题？

A：导致每次对话都是独立会话，无法实现真正的多轮对话，改进方案：

1. 会话级记忆：按 `session_id` 隔离记忆
2. 持久化存储：使用 Redis/数据库保存历史
3. 分层记忆：工作记忆（当前任务） + 长期记忆（跨会话知识）



Q: `MemoryManager` 的 `max_memory=10` 设计合理吗？如何动态调整？

A：不合理原因

1. 一次 ReAct 循环包含 3 条消息（assistant + tool + assistant），10 条只能保存 3 轮
2. System Prompt 也占用一个槽位
3. 固定数量无法应对不同 token 限制的模型



Q: 如果工具执行超时或失败，Agent 会陷入死循环吗？

A：当前机制

- agent.py:132 捕获异常并将错误信息返回给 LLM
- 但没有记录失败次数，可能导致 LLM 反复调用同一个错误工具

改进方案：达到 max_step 限制

```
class ToolFailureTracker:
    def __init__(self, max_failures_per_tool: int = 3):
        self.failures: Dict[str, int] = {}
        self.max_failures = max_failures_per_tool
    
    def record_failure(self, tool_name: str):
        self.failures[tool_name] = self.failures.get(tool_name, 0) + 1
        if self.failures[tool_name] >= self.max_failures:
            raise ToolExecutionError(f"工具 {tool_name} 失败次数过多，已禁用")
```

------

> LLM 调用类问题

Q：流式输出模式下，如何处理 `tool_calls` 的拼接？为什么要用 `index` 字段？

A：示例流失输出格式

```
// 第一个 chunk
{"delta": {"tool_calls": [{"index": 0, "id": "call_123", "function": {"name": "get_weather"}}]}}

// 第二个 chunk
{"delta": {"tool_calls": [{"index": 0, "function": {"arguments": "{\"loc"}}]}}

// 第三个 chunk
{"delta": {"tool_calls": [{"index": 0, "function": {"arguments": "ation\":"}}]}}

// 第四个 chunk（如果有多个工具调用）
{"delta": {"tool_calls": [{"index": 1, "id": "call_456", "function": {"name": "search"}}]}}
```

处理逻辑：

1. `index` 标识是哪个工具调用（可能并行调用多个）
2. 第一个 chunk 包含 `id` 和 `name`
3. 后续 chunk 只包含 `arguments` 片段，需要拼接



Q：打印 `reasoning_content` 但不保存，这样设计的原因？

A：如果保存到上下文，会占用大量 tokens，类似 OpenAI 的 `o1` 模型的 `<think>` 标签，只展示给用户看，不参与对话历史。

------

> 工具系统类问题

Q：`_get_param_type_for_tool_schema()` 为什么用递归实现？性能如何？

A：递归原因： 处理嵌套类型（如 `List[Dict[str, List[int]]]`）时，递归是最自然的方式

性能分析：

- 时间复杂度：O(n)，n 为类型嵌套深度
- 实际场景中 n ≤ 5，性能可接受
- 递归深度不会超过 Python 默认限制（1000）

可能的问题：

```
# 循环引用类型（极端情况）
from typing import ForwardRef
MyType = List['MyType']  # 会导致无限递归
```

防御措施：

```
def _get_param_type_for_tool_schema(
    self,
    type_hint: Type,
    visited: Optional[Set] = None
) -> Dict[str, Any]:
    if visited is None:
        visited = set()
    
    type_id = id(type_hint)
    if type_id in visited:
        return {"type": "object"}  # 检测到循环引用
    
    visited.add(type_id)
    # ... 递归逻辑
```

------

> 记忆系统类问题

Q：`memory_manager.py` 为什么继承 `BaseModel`？不继承有什么问题？

A：继承 Pydantic BaseModel 的好处

1. 自动类型校验

   ```
   # 如果传入错误类型，Pydantic 会自动转换或报错
   memory_manager = MemoryManager(max_memory="10")  # ✅ 自动转换为 int
   memory_manager = MemoryManager(max_memory="abc")  # ❌ 抛出 ValidationError
   ```

2. 序列化/反序列化

   ```
   # 导出为 JSON
   data = memory_manager.model_dump()
   json_str = memory_manager.model_dump_json()
   
   # 从 JSON 恢复
   restored = MemoryManager.model_validate_json(json_str)
   ```

3. 配置管理

   ```
   # 从环境变量加载
   class Config(BaseModel):
       max_memory: int = Field(default=10, env="MAX_MEMORY")
   
   config = Config()  # 自动读取 MAX_MEMORY 环境变量
   ```

不继承的问题：

- 需要手写 `__init__`
- 缺少类型校验（如 memory_manager.py:50 测试代码传入 `13.234` 不会报错）

------

> ReAct 框架类问题

Q: `think()` 和 `act()` 的边界如何划分？为什么不合并为一个方法？

A：分离原因：

1. 职责单一原则

- `think()`: 调用 LLM 决策（规划阶段）
- `act()`: 执行工具（行动阶段）

2. 支持不同的执行策略

```python
# 策略 1: ReAct（当前实现）
async def run_step(self):
    should_act = await self.think()
    if should_act:
        await self.act()

# 策略 2: Plan-Execute
async def run_step(self):
    plan = await self.think()  # 一次性生成完整计划
    for action in plan:
        await self.act(action)  # 批量执行

# 策略 3: Tree of Thoughts
async def run_step(self):
    candidates = await self.think_multiple()  # 生成多个可能的思路
    best = self.evaluate(candidates)
    await self.act(best)
```

3. 方便插入中间件

```python
async def run_step(self):
    # 思考前：加载上下文
    context = await self.context_manager.retrieve(query)
    
    # 思考
    should_act = await self.think(context)
    
    # 思考后：记录日志
    logger.info(f"LLM decision: {should_act}")
    
    # 行动前：权限检查
    if should_act:
        await self.permission_checker.verify(tool_calls)
        await self.act()
```



Q：如果 LLM 陷入"思考-行动"死循环怎么办？

A：当前为限制最大步数，改进方案为 1）检测重复使用；2）强制终止 + 回退



Q: 为什么最后总结阶段要设置 `tool_choice="none"`？

A：最后一步是生成总结性回复，不需要再调用工具，OpenAI 文档说明：

- `tool_choice="auto"`: 模型自行决定是否调用工具（默认）
- `tool_choice="none"`: 强制不调用工具
- `tool_choice={"type": "function", "function": {"name": "xxx"}}`: 强制调用特定工具





## 架构分析

### 一、整体架构重构方案

#### 1、引入分层架构模式

当前问题：模块间耦合度较高，缺少清晰的职责边界

优化方案：采用六边形架构（Ports & Adapters）

```
┌─────────────────────────────────────────────────────────┐
│                    应用层 (Application)                   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  AgentOrchestrator (编排器)                      │   │
│  │  - 协调 LLM、Tool、Memory 的交互                 │   │
│  │  - 管理 Agent 生命周期                           │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
          ↓              ↓              ↓
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  LLM Port   │  │  Tool Port  │  │ Memory Port │  ← 接口层
└─────────────┘  └─────────────┘  └─────────────┘
      ↓                ↓                ↓
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│OpenAI/Qwen  │  │FunctionTool │  │ Redis/Mem   │  ← 适配器层
│  Adapter    │  │MCP Adapter  │  │  Adapter    │
└─────────────┘  └─────────────┘  └─────────────┘

```



#### 2、引入策略模式管理记忆

当前问题：记忆管理过于简单，无法应对复杂场景

优化方案：多层记忆架构 + 策略模式

```
from enum import Enum
from typing import Protocol

class MemoryStrategy(str, Enum):
    SLIDING_WINDOW = "sliding_window"      # 滑动窗口
    TOKEN_BASED = "token_based"            # 基于 Token 数量
    SEMANTIC_COMPRESSION = "semantic"      # 语义压缩
    HIERARCHICAL = "hierarchical"          # 分层记忆

class ICompressionStrategy(Protocol):
    async def compress(self, messages: List[Dict]) -> List[Dict]:
        ...

class TokenBasedStrategy(ICompressionStrategy):
    """基于 Token 限制的压缩策略"""
    def __init__(self, max_tokens: int = 4000, tokenizer: str = "cl100k_base"):
        self.max_tokens = max_tokens
        self.tokenizer = tiktoken.get_encoding(tokenizer)
    
    async def compress(self, messages: List[Dict]) -> List[Dict]:
        total_tokens = 0
        compressed = []
        
        # 反向遍历，优先保留最新消息
        for msg in reversed(messages):
            msg_tokens = len(self.tokenizer.encode(msg["content"]))
            if total_tokens + msg_tokens > self.max_tokens:
                # 对旧消息进行摘要
                summary = await self._summarize(compressed)
                return [{"role": "system", "content": f"[历史摘要] {summary}"}] + compressed
            compressed.insert(0, msg)
            total_tokens += msg_tokens
        
        return compressed

class HierarchicalMemory:
    """分层记忆系统"""
    def __init__(
        self,
        working_memory_size: int = 10,      # 工作记忆（最近对话）
        vector_store: Optional[VectorStore] = None  # 长期记忆（向量检索）
    ):
        self.working_memory: List[Dict] = []
        self.episodic_memory: List[Dict] = []  # 情景记忆（完整会话）
        self.semantic_memory = vector_store     # 语义记忆（知识图谱）
        self.working_memory_size = working_memory_size
    
    async def add_message(self, message: Dict):
        self.working_memory.append(message)
        self.episodic_memory.append(message)
        
        # 工作记忆满时，压缩到语义记忆
        if len(self.working_memory) > self.working_memory_size:
            archived = self.working_memory.pop(0)
            if self.semantic_memory:
                await self.semantic_memory.add(
                    text=archived["content"],
                    metadata={"role": archived["role"], "timestamp": time.time()}
                )
    
    async def retrieve_relevant(self, query: str, top_k: int = 3) -> List[Dict]:
        """检索相关记忆"""
        if not self.semantic_memory:
            return self.working_memory
        
        # 混合检索：工作记忆 + 语义检索
        semantic_results = await self.semantic_memory.search(query, top_k=top_k)
        return self.working_memory + semantic_results

```



#### 3、增强工具系统：支持异步、超时、重试

当前问题：工具执行缺少容错机制

优化方案：工具执行中间件链



#### 4、可观测性系统：Tracing + Metrics + Logging

当前问题：无法追踪 Agent 执行过程，难以调试和优化

优化方案：集成 OpenTelemetry



#### 5、Agent 编排：支持多 Agent 协作

当前问题：单一 Agent，无法处理复杂任务

优化方案：Multi-Agent 编排器

```
from enum import Enum
from typing import List, Dict, Optional

class AgentRole(str, Enum):
    PLANNER = "planner"          # 规划者
    RESEARCHER = "researcher"    # 研究员
    CODER = "coder"             # 编码者
    REVIEWER = "reviewer"       # 审查者

class AgentMessage(BaseModel):
    from_agent: AgentRole
    to_agent: AgentRole
    content: str
    metadata: Dict = Field(default_factory=dict)

class MultiAgentOrchestrator:
    """多 Agent 编排器"""
    
    def __init__(self):
        self.agents: Dict[AgentRole, ToolCallingAgent] = {}
        self.message_bus: List[AgentMessage] = []
    
    def register_agent(self, role: AgentRole, agent: ToolCallingAgent):
        self.agents[role] = agent
    
    async def execute_task(self, user_query: str) -> str:
        """
        执行流程:
        1. Planner 分解任务
        2. Researcher 收集信息
        3. Coder 实现代码
        4. Reviewer 审查结果
        """
        
        # Step 1: 规划
        plan_message = [
            {"role": "system", "content": "你是任务规划专家，将复杂任务分解为子任务"},
            {"role": "user", "content": user_query}
        ]
        plan_result = await self.agents[AgentRole.PLANNER].run(plan_message)
        
        # Step 2: 研究
        research_message = [
            {"role": "system", "content": "你是研究员，负责收集相关信息"},
            {"role": "user", "content": f"根据以下计划收集信息：\n{plan_result}"}
        ]
        research_result = await self.agents[AgentRole.RESEARCHER].run(research_message)
        
        # Step 3: 实现
        coding_message = [
            {"role": "system", "content": "你是程序员，负责编写代码"},
            {"role": "user", "content": f"根据以下资料实现功能：\n{research_result}"}
        ]
        code_result = await self.agents[AgentRole.CODER].run(coding_message)
        
        # Step 4: 审查
        review_message = [
            {"role": "system", "content": "你是代码审查员，负责检查代码质量"},
            {"role": "user", "content": f"审查以下代码：\n{code_result}"}
        ]
        final_result = await self.agents[AgentRole.REVIEWER].run(review_message)
        
        return final_result

```



### 二、性能优化方案

#### 1、并行工具调用

当前问题：agent.py:99 顺序执行工具，效率低

优化方案：

```
async def act_parallel(self, message: Dict) -> bool:
    """并行执行独立工具"""
    tool_calls = message["tool_calls"]
    
    # 分析工具依赖关系
    dependency_graph = self._build_dependency_graph(tool_calls)
    
    # 按拓扑排序分批执行
    for batch in self._topological_sort(dependency_graph):
        tasks = [
            self._execute_single_tool(tool_call)
            for tool_call in batch
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        for tool_call, result in zip(batch, results):
            if isinstance(result, Exception):
                logger.error(f"工具 {tool_call['function']['name']} 执行失败: {result}")
            else:
                self.memory_manager.add_message({
                    "role": "tool",
                    "content": result,
                    "tool_call_id": tool_call["id"]
                })

```



#### 2、LLM 响应缓存

```
import hashlib
from cachetools import TTLCache

class CachedLLM(LLM):
    def __init__(self, *args, cache_ttl: int = 3600, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = TTLCache(maxsize=1000, ttl=cache_ttl)
    
    def _compute_cache_key(self, messages: List[Dict], **kwargs) -> str:
        """计算缓存键"""
        content = json.dumps(messages, sort_keys=True) + json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    async def chat(self, messages: List[Dict], **kwargs) -> Dict:
        cache_key = self._compute_cache_key(messages, **kwargs)
        
        if cache_key in self.cache:
            logger.info("命中 LLM 缓存")
            return self.cache[cache_key]
        
        response = await super().chat(messages, **kwargs)
        self.cache[cache_key] = response
        return response

```



### 三、安全性增强

1、工具权限控制

2、输入验证与沙箱执行
