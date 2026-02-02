OpenAI过去的API：

- https://github.com/openai/openai-python
- https://platform.openai.com/docs/api-reference/introduction



OpenAI于2025年3月发布OpenAI Agent SDK

官网：

- https://openai.github.io/openai-agents-python/quickstart/
- https://github.com/openai/openai-agents-python

官网写的很清晰，学完agent示例后，剩下内容可以先看Github，后看官网



环境配置

```bash
# 在当前文件夹下创建uv环境，并指定python版本
uv venv --python 3.12
uv init

uv add openai-agents
```



核心组件:

1. 智能体配置 [**Agents**](https://openai.github.io/openai-agents-python/agents): LLMs configured with instructions, tools, guardrails, and handoffs
2. 任务委托 [**Handoffs**](https://openai.github.io/openai-agents-python/handoffs/): A specialized tool call used by the Agents SDK for transferring control between agents
3. 安全校验 [**Guardrails**](https://openai.github.io/openai-agents-python/guardrails/): Configurable safety checks for input and output validation
4. [**Sessions**](https://github.com/openai/openai-agents-python#sessions): Automatic conversation history management across agent runs
5. 执行追踪 [**Tracing**](https://openai.github.io/openai-agents-python/tracing/): Built-in tracking of agent runs, allowing you to view, debug and optimize your workflows



#### LLM示例

示例代码：

```python
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")


client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

# models_list = client.models.list()
# print(models_list.data)

responce = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Tell me a joke"},
    ]
)

print(responce.choices[0].message.content)

```



#### Agent示例

示例代码：

```python
from openai import AsyncOpenAI, OpenAI
from agents import Agent, Runner
from agents import OpenAIChatCompletionsModel, set_default_openai_client, set_tracing_disabled
from agents.model_settings import ModelSettings
from agents import WebSearchTool

from pydantic import BaseModel
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

# 创建client
external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

# 设置client为默认client
set_default_openai_client(external_client)
set_tracing_disabled(True)

async def main():
    agent = Agent(
        name="Assistant",
        instructions="Answer the following questions as best you can.",
        model=OpenAIChatCompletionsModel(
            model="openai/gpt-4o-mini",
            openai_client=external_client,
        )
    )

    result = await Runner.run(agent, "What is the capital of France?")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())

```

示例结果：

```python
RunResult:
- Last agent: Agent(name="Assistant", ...)
- Final output (str):
    The capital of France is Paris.
- 1 new item(s)
- 1 raw response(s)
- 0 input guardrail result(s)
- 0 output guardrail result(s)
(See `RunResult` for more details)
```

备注：虽然设置了默认client，但是Agent中依旧要指定openai_client，二者一个也不能删，具体原因暂时没理清



#### Multi-Agent示例

基于Workflow的DeepResearch参考：https://www.bilibili.com/video/BV1PoLjzVEbx

本质上就是写几个agent，指定每个agent的输出格式，再写一个run函数，最后顺序执行、并将几个agent的输入与输出串起来。



Handoffs example：

```python
from agents import Agent, Runner
from agents import OpenAIChatCompletionsModel, set_default_openai_client, set_tracing_disabled
from openai import AsyncOpenAI
import asyncio

import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

# 创建client
external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

# 设置client为默认client
set_default_openai_client(external_client)
set_tracing_disabled(True)

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You only speak Spanish.",
    model=OpenAIChatCompletionsModel(
            model="openai/gpt-4o-mini",
            openai_client=external_client,
    )
)

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
    model=OpenAIChatCompletionsModel(
            model="openai/gpt-4o-mini",
            openai_client=external_client,
    )
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent],
    model=OpenAIChatCompletionsModel(
            model="openai/gpt-4o-mini",
            openai_client=external_client,
    )
)


async def main():
    result = await Runner.run(triage_agent, input="Hola, ¿cómo estás?")
    print(result.final_output)
    # ¡Hola! Estoy bien, gracias por preguntar. ¿Y tú, cómo estás?


if __name__ == "__main__":
    asyncio.run(main())
```

示例结果：

```python
¡Hola! Estoy aquí para ayudarte. ¿En qué puedo asistirte hoy?
```

