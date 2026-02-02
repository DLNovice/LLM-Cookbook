

# 快速上手

```bash
pip install litellm
```

```bash
litellm --config /path/to/config.yaml
```

```bash
model_list:
  - model_name: gemini-2.0-flash
    litellm_params:
      model: openrouter/google/gemini-2.0-flash-001
      api_base: https://openrouter.ai/api/v1
      api_key: "**************"
      api_version: "2025-01-01-preview" # [OPTIONAL] litellm uses the latest azure api_version by default
```



```bash
curl -X POST 'http://0.0.0.0:4000/chat/completions' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer sk-1234' \
-d '{
    "model": "gemini-2.0-flash",
    "messages": [
      {
        "role": "system",
        "content": "You are an LLM named gpt-4o"
      },
      {
        "role": "user",
        "content": "what is your name?"
      }
    ]
}'
```



# 使用经验

#### litellm与LangChain

部分场景下，对litellm模型服务的支持并不完善，相比对OpenAI等官方服务的支持，会缺少一些功能。

不过或许可以套别人的壳子。

比如Litellm与LangChain，litellm 本质上是一个 **兼容 OpenAI API 协议的代理**，只要它对外暴露的接口遵循 `/v1/chat/completions` 规范，就可以直接在 LangChain 里用：

```python
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4",  # 这里的名字要和 litellm 配置的别名一致
    openai_api_key="fake-key",  # 可以随便填一个
    openai_api_base="http://localhost:4000"  # 你的 litellm proxy 地址
)

response = llm.predict("你好，可以帮我写一首小诗吗？")
print(response)
```

扩展：自定义 LangChain LLM Wrapper

在编程里，**wrapper（封装器）** 就是把一个已有的功能（比如 litellm 的 API 调用）“包”在一个类或函数里，让它在别的框架里能像原生支持的一样使用。

举个比喻：

- LangChain 只认识 “OpenAI 风格” 的 LLM 接口。
- litellm 其实能代理很多模型，但它对 LangChain 来说是个“陌生人”。
- 我们写一个 **wrapper 类**，让 litellm 伪装成 LangChain 能理解的 `LLM`，这样就能无缝接入。



案例 - 把 litellm 的接口包装成 LangChain 的 `LLM`

```python
from langchain.llms.base import LLM
from typing import Any, List, Optional
import requests


class LiteLLMWrapper(LLM):
    api_base: str
    model: str
    api_key: Optional[str] = None

    @property
    def _llm_type(self) -> str:
        return "litellm"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # 这里假设 litellm 提供 OpenAI 兼容的 /v1/chat/completions
        response = requests.post(
            f"{self.api_base}/v1/chat/completions",
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
            },
            headers=headers,
            timeout=60,
        )

        data = response.json()
        return data["choices"][0]["message"]["content"]


# 初始化 LLM
llm = LiteLLMWrapper(
    api_base="http://localhost:4000",  # 你的 litellm proxy 地址
    model="gpt-3.5-turbo",
    api_key="fake-key"  # 如果 litellm 配置需要的话
)

# 直接调用
print(llm("帮我写一个 SQL 查询，选出所有用户的名字"))
```

还能和 LangChain 的 **Agent**、**Chain** 等组件搭配：

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

prompt = PromptTemplate.from_template("请用一句话总结: {text}")

chain = LLMChain(llm=llm, prompt=prompt)

print(chain.run("LangChain 是一个强大的框架，用于构建基于大语言模型的应用。"))
```



案例 - 如果 litellm 返回结果和 OpenAI 有差异，或者你想调用它的一些额外功能（比如多模型路由、fallback），可以写一个继承自 `LLM` 的自定义类

```python
from langchain.llms.base import LLM
from typing import Any, List, Optional
import requests

class LiteLLM(LLM):
    api_base: str
    model: str
    api_key: Optional[str] = None

    @property
    def _llm_type(self) -> str:
        return "litellm"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        response = requests.post(
            f"{self.api_base}/v1/completions",
            json={"model": self.model, "prompt": prompt},
            headers=headers
        )
        return response.json()["choices"][0]["text"]


llm = LiteLLM(api_base="http://localhost:4000", model="gpt-3.5-turbo")
print(llm("帮我写一个SQL查询语句"))
```

