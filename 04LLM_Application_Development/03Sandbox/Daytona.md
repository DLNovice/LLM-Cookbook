> 官网：https://github.com/daytonaio/daytona
>
> Run AI Code. Secure and Elastic Infrastructure for Running Your AI-Generated Code.



### 快速入门

> 概述：去Daytona官网申请key，然后运行示例代码（创建沙盒、运行程序）

环境配置：

```
uv venv --python 3.12
source .venv/bin/activate
uv pip install daytona
```

示例代码：暂时无法避开API_KEY

```python
from daytona import Daytona, DaytonaConfig, CreateSandboxBaseParams

# Initialize the Daytona client
daytona = Daytona(DaytonaConfig(api_key="YOUR_API_KEY"))

# Create the Sandbox instance
sandbox = daytona.create(CreateSandboxBaseParams(language="python"))

# Run code securely inside the Sandbox
response = sandbox.process.code_run('print("Sum of 3 and 4 is " + str(3 + 4))')
if response.exit_code != 0:
    print(f"Error running code: {response.exit_code} {response.result}")
else:
    print(response.result)

# Clean up the Sandbox
daytona.delete(sandbox)
```



### 入门指南

Daytona具备设置沙箱环境性能配置、预安装环境等等操作，详情参考官网文档。

