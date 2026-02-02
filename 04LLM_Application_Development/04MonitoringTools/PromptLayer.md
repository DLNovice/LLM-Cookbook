PromptLayer是一款专注于提示工程的平台，能够帮助开发者更好地管理和优化其提示。它还提供了LLM可观察性，方便用户可视化请求、版本化提示以及跟踪使用情况。



官网：https://dashboard.promptlayer.com/



环境配置：

```
pip install promptlayer
```



账号：***@qq.com

密码：123456789@Abcdef



示例代码：

```
import promptlayer # Don't forget this 🍰
from langchain.callbacks import PromptLayerCallbackHandler

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

llm = ChatOpenAI(
    model="google/gemini-2.0-flash-001",
    base_url="https://openrouter.ai/api/v1",
    api_key="sk-or-v1-******",
    streaming=True,
    callbacks=[PromptLayerCallbackHandler(
        pl_tags=["langchain"]
    )],
)
llm_results = llm(
    [
        SystemMessage(content="You are a funny AI comedian."),
        HumanMessage(content="What comes after 1,2,3 ?"),
    ]
)
print(llm_results)
```

代码缺少key，暂时没看懂此框架怎么用的