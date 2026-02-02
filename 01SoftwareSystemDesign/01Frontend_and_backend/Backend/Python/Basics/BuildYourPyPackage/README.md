下面是一份从零开始编写、发布、维护 Python 库的完整全流程教程



### 1、创建你的项目结构

一个标准、专业的 Python 包结构如下：

```python
demo_package/
│
├── src/
│   └── demo_package/
│       ├── __init__.py
│       ├── core.py
│       └── utils.py
│
├── tests/
│   └── test_core.py
│
├── README.md
├── pyproject.toml
├── LICENSE
├── .gitignore
└── CHANGELOG.md
```



### 2、初始化项目

1）创建目录

```bash
mkdir demo_package && cd demo_package
mkdir -p src/demo_package tests
touch src/demo_package/__init__.py
```

2）初始化 Git（可选，但强烈建议）

```bash
git init
```



### 3、编写你的库的代码

例如写一个简单的数学函数：

**src/demo_package/core.py**

```python
def add(a: float, b: float) -> float:
    return a + b
```

**src/demo_package/\**init\**.py**

```python
from .core import add

__all__ = ["add"]
```



### 4、为你的库编写测试

Python库的行业标准测试框架：pytest

安装：

```bash
pip install pytest
```

测试文件：

**tests/test_core.py**

```python
from demo_package import add

def test_add():
    assert add(1, 2) == 3
```

运行测试：

```
pytest
```



### 5、写 README.md

包含：

- 介绍
- 安装方法
- 使用示例
- API 说明

示例：

~~~markdown
# demo_package

一个用于数学运算的简单 Python 库。

## 安装

```bash
pip install demo_package
~~~



### 6、添加许可证 LICENSE

略



### 7、配置 pyproject.toml（最重要一步）

示例：

```toml
[project]
name = "demo_package"
version = "0.1.0"
description = "A simple math library."
readme = "README.md"
requires-python = ">=3.8"
authors = [
    { name="Your Name", email="you@example.com" }
]
license = {file = "LICENSE"}

[project.urls]
"Homepage" = "https://github.com/yourname/demo_package"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

```

备注：

- 注意添加`[tool.setuptools.packages.find]`，因为我`demo_package`外面又套了层名为`demo_package`的目录，导致build时，找根目录去了，而非src目录



### 8、构建

安装构建工具：`pip install build`

执行构建：`python -m build  `

```bash
> python -m build    
* Creating isolated environment: venv+pip...
* Installing packages in isolated environment:
  - setuptools>=61.0
* Getting build dependencies for sdist...
.....
removing build\bdist.win-amd64\wheel
Successfully built demo_package-0.1.0.tar.gz and demo_package-0.1.0-py3-none-any.whl
```

构建后会生成：

```bash
dist/
    demo_package-0.1.0.tar.gz
    demo_package-0.1.0-py3-none-any.whl
```



如果构建失败，直接删除旧的构建产物：

```bash
rm -r dist
rm -r build
rm -r *.egg-info
```

然后重新构建即可：`python -m build`



### 9、使用示例

安装：

```bash
pip install .\dist\demo_package-0.1.0-py3-none-any.whl
```

示例代码：

```python
from demo_package import add

print(add(3, 5))
```

示例结果：

```python
> python .\demo.py
8
```



### 10、上传到 PyPI

> 未尝试

先安装 twine：

```bash
pip install twine
```

上传：

```bash
twine upload dist/*
```

如果你需要测试上传到 TestPyPI：

```bash
twine upload -r testpypi dist/*
```



### 11、如何升级版本

修改 `pyproject.toml`：

```toml
version = "0.2.0"
```

然后重新：

```bash
python -m build
twine upload dist/*
```

遵循 SemVer 版本规范：

- 修复 bug → 0.1.1
- 新增功能（兼容）→ 0.2.
