LangSmith不能本地部署，在云端申请key：https://smith.langchain.com/



环境配置：

```
pip install -U langchain langchain-openai
pip install -U langsmith
```



示例代码：

```
import os
from langchain_openai import ChatOpenAI

os.environ['LANGSMITH_TRACING']="true"
os.environ['LANGSMITH_ENDPOINT']="https://api.smith.langchain.com"
os.environ['LANGSMITH_API_KEY']="lsv2_pt_******"
os.environ['LANGSMITH_PROJECT']="pr-impassioned-baseline-5"


llm = ChatOpenAI(
            model="google/gemini-2.0-flash-001",
            base_url="https://openrouter.ai/api/v1",
            api_key="sk-or-v1-******",
)
llm.invoke("Hello, world!")
```

示例效果：

![image-20250812161458754](./assets/image-20250812161458754.png)