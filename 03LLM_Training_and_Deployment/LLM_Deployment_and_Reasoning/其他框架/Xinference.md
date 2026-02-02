# 01 安装Xinference

参考：

- https://blog.csdn.net/vvc_a/article/details/141196329



## 方法一：直接部署

1、创先虚拟环境

```
# 创建一个环境
conda create -n xinference python=3.10.15 
# 激活环境
conda activate xinference
```



2、安装环境

```
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple "xinference[all]"
```



3、启动Xinference

```
# 前台
xinference-local --host 0.0.0.0 --port 9997

# 后台
nohup xinference-local --host 0.0.0.0 --port 9997 & > output.log
```

注意：

- Windows 上不支持用 0.0.0.0 启动，应使用 IP，比如127.0.0.1，否则会出现`RuntimeError: Cluster is not available after multiple attempts`
- Xinference 默认是从 [HuggingFace](https://huggingface.co/models) 上下载模型，如果需要使用其他网站下载模型，可以通过设置环境变量`XINFERENCE_MODEL_SRC`来实现，如使用modelscope：`XINFERENCE_MODEL_SRC=modelscope xinference-local --host 0.0.0.0 --port 9997`



## 方法二：docker部署

```
docker run  -p 9997:9997 --gpus all xprobe/xinference:latest xinference-local -H 0.0.0.0
```



# 02 配置大模型

### 1、在线配置

参考：https://blog.csdn.net/magic_ll/article/details/144689516

等待安装即可

![image-20250116155757885](./assets/image-20250116155757885.png)

此时在终端可以看到下载进度：

![image-20250116160410959](./assets/image-20250116160410959.png)

等待模型自动下载、配置完成后，可在Running Models栏看到该模型：

![image-20250120094423693](./assets/image-20250120094423693.png)



常见问题：

- 重启Xinference服务后，模型丢失问题：重启后，模型需要重新加载
  - 如果模型是直接通过Xinference前端加载的，那么直接重新走一遍流程即可，xinference前端也会显示此模型使用过
    <img src="./assets/image-20250120110950437.png" alt="image-20250120110950437" style="zoom: 25%;" />
  - 如果是终端配置的模型，流程和上述一致，也可以在xinference前端看到此模型使用过，比如如下一个embedding模型，我这里直接给出模型路径，然后重新加载即可
    <img src="./assets/image-20250120111413239.png" alt="image-20250120111413239" style="zoom:25%;" />
- xinference更换端口（非默认的9997）启动后，xinference list出现连接问题：
  - 
- https://blog.csdn.net/TZfool/article/details/141352701
  - 补充：上述文章的方案是修改Quantization，不过我尝试修改Model Format，发现也是可行的
    ![image-20250120093916119](./assets/image-20250120093916119.png)
- qwen模型，只要选择了量化，就无法使用，很奇怪，glm4也尝试选了int8模型，模型无法导入，尝试选择none，模型可用，但是只调用cpu资源不调用gpu



### 2、终端配置

如：`xinference launch --model-name bge-large-zh --model-type embedding`

![image-20250120094512434](./assets/image-20250120094512434.png)



### 3、离线配置

参考如下博客中的做法：本地下载，前端导入

- https://blog.csdn.net/u010800804/article/details/141756410



# 03 Xinference + Vllm

官方源码：https://github.com/xorbitsai/inference/tree/main/xinference/model/llm/vllm

源码解析如下：

核心的就是`xinference/model/llm/vllm/core.py`了

**（1）vLLM引擎的抽象封装**

定义了`VLLMModel`类（继承自`LLM`基类），通过**分层抽象**将vLLM的核心功能封装为Xinference的标准接口。



**（2）推理请求处理流程**

Xinference通过**异步任务队列**处理推理请求，核心调用链如下：

```
async def generate(self, prompt: str, params: Dict) -> Dict:
    # 1. 参数转换
    sampling_params = self._convert_params(params)  
    
    # 2. 调用vLLM异步引擎
    outputs = await self._llm.generate(
        prompts=[prompt], 
        sampling_params=sampling_params,
        use_tqdm=False
    )
    
    # 3. 结果标准化
    return self._format_response(outputs)
```

关键优化：

1. 批处理调度：通过`prompts`列表支持多请求合并，利用vLLM的PagedAttention优化吞吐量

2. 内存复用：使用vLLM的BlockManager缓存KVCache块，动态分配物理块给不同请求

3. 流式输出：通过`asyncio.Stream`实现Token级流式传输（需配合vLLM的`stream`参数）。



**（3）与Xinference框架的深度集成**

1. 模型加载
    通过`ModelRegistry`注册vLLM支持模型，自动下载HuggingFace/Modelscope模型：

   ```
   def register_vllm_models():
       for model_spec in VLLM_MODELS:
           register_llm(model_spec, VLLMModel, override=True)
   ```

2. 资源管理
    使用`ResourceManager`跟踪GPU内存使用，实现动态扩缩容：

   ```
   def _check_resources(self):
       if not torch.cuda.is_available():
           raise ResourceNotEnough("CUDA device required for vLLM")
   ```

3. 监控指标
    暴露Prometheus指标（Tokens/s, Latency等）：

   ```
   self.metrics.add_metric('vllm_batch_size', len(prompts))
   ```



**（4）性能优化策略**

1. Prefix Caching：对重复前缀进行缓存，通过prefix_caching参数减少重复计算
2. Quantization支持：自动识别GGML/GPTQ等量化格式，加载适配的vLLM内核；
3. 自定义OP：集成FlashAttention-2等定制CUDA Kernel提升计算效率。
