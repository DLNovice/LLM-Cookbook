本章核心在于`01Basic-Knowledge-of-LLM`中的课程笔记，其他目录基本无实质内容。



# 资源补充

LLM教程层出不穷，除了本目录已列的笔记，还有些其他资源：

- datawhale系列课 happy-llm：https://github.com/datawhalechina/happy-llm
- datawhale系列课 Hello-Agents：https://datawhalechina.github.io/hello-agents
- mlabonne：https://github.com/mlabonne/llm-course

- 浙大教材：https://github.com/ZJU-LLMs/Foundations-of-LLMs

- 一些实战：https://github.com/liguodongiot/llm-action?tab=readme-ov-file

- 沐神的论文精读：https://github.com/mli/paper-reading

- 一些开发工程性的东西：https://github.com/echonoshy/cgft-llm

其他：

- LLaMA2模型搭建：[万字长文教你训练一个Transformer 小模型（上）](https://mp.weixin.qq.com/s/u8PuRShsUMv8nxefnFoGkA)



# 一些补充

> 一些篇幅较长的内容放在Snippets目录下了

#### 为什么同样的问题，模型回答结果不一致？

参考Open AI 前 CTO Mira Murati的爆火文章

- https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/
- https://mp.weixin.qq.com/s/Xv32OYDaH0aN2_LWLP9A-Q?scene=1

一些解读：

- https://mp.weixin.qq.com/s/RQxJqPAHXPSXj0QQWOdy8A
- （推荐）https://mp.weixin.qq.com/s/pBpf4BQqrOZJX3sA-fFdEg

简述：

- 在此之前，社区有一个广为流传的关于这个“通病”的主流假说—**“并发 + 浮点”理论。**
  - **第一，是浮点计算的非结合性导致的**，由于计算机存在舍入误差，数学上 (a+b)+c = a+(b+c) 的绝对相等，在浮点数世界里会变成约等，而计算顺序的改变，会带来结果上“位级别”的微小差异。
  - **第二，是GPU并行计算决定的：**为了追求极致速度，GPU 会同时派出成百上千个核心（kernel）去执行求和等归约操作。谁先算完、谁后算完，这个计算的顺序在每次运行时都是不可预测的。
- 不过，Thinking Machines Lab 发布的《克服 LLM 推理中的不确定性》论文博客提出了质疑。他们认为，问题不在“有没有并行/浮点”。
- 研究团队认为不确定性来自**什么时候归约顺序会被改写。**所以论文将矛头指向了一个更高阶的系统设计缺陷：**批次不变性 (Batch Invariance，问题出在模型如何同时处理多个请求) 的缺失**。
- 通俗的说，你向 AI 提问，得到的结果，理论上不应该因为和你一同被处理的还有 3 个人还是 30 个人（即批次大小）而有所不同。

PS：实验的最后修改了vLLM，使1000次采样的回答一致，类似的对vLLM的二次开发能力在市场上需求大吗？



下文有些让大模型的回答，有点类似于社区的“并发 + 浮点”理论。

------

一个**小学生也能懂的版本**：

1. **小数算不准**
    电脑里算数用的是“浮点数”，有点像用小数点后只能写几位。如果先加谁、后加谁，结果可能会差一点。
2. **排队方式不一样**
    模型要同时回答很多人问题。像食堂打饭，一会儿一人一碗，一会儿几个人一起打。顺序不一样，里面的计算步骤就会变。
3. **分工不同**
    模型在大脑里算数时，会把任务切成小块分给很多工人（GPU）。工人怎么分组、怎么合作，如果换了方式，最后答案也可能有点差别。

怎么解决？

- 让模型“不管多少人一起排队，计算方式都一样”。
- 规定好计算的顺序，不让它随便换。

这样，就能让模型每次回答更稳定。

------

两篇资料共同指向一个核心结论：**大模型生成结果不一致，本质是「概率采样」与「硬件-软件-数据」多层噪声叠加所致**。可拆成 5 个层级：

1. 算法层：token 采样策略
   训练目标只是让模型学会「下一个 token 的概率分布」；真正解码时，如果 temperature>0 或 top-p/top-k<1，就会从分布里「随机挑」一个 token。同一输入、同一模型，只要随机种子不同，分支就会越走越远，最终答案看起来“完全不一样”。
2. 实现层：并行算子带来的非结合误差
   注意力、softmax、LayerNorm、矩阵乘都会用到 float16/bfloat16。GPU 线程块划分、归约顺序、CUDA kernel 版本、甚至 cuBLAS/cuDNN 的启发式选择，都可能让同一矩阵乘法出现 1–2 ulp 的误差。这些微观误差经过几十层放大，可能把“概率排名第 2 的 token”推到第 1 位，采样结果就此分叉。——这就是 Thinking Machines 博客里用“ablation”强行固定随机种子仍观察到 2–4 % 不一致率的根因。
3. 框架/硬件层：不可控并发
   多卡 tensor parallel、pipeline parallel 时，每次微批大小、网络延迟、GPU Boost 频率、显存碎片都能改变 kernel launch 顺序；cuDNN 的 benchmark 模式会为同一卷积选不同 algos。即使把 PyTorch 的 `torch.use_deterministic_algorithms(True)` 打开，目前仍有 20+ 个算子（FlashAttention、稀疏矩阵乘等）没有确定型实现。
4. 数据层：动态上下文
   在对话或 RAG 场景，外部检索结果、系统 prompt、时间戳、用户昵称每次都会变，模型看到的 prompt 已不同，结果自然“漂移”。
5. 模型更新层：权重热更新
   线上系统常做滚动部署、A/B 实验、LoRA/adapter 热插拔，两次请求可能打到不同权重，用户感知就是“同一问题答案变”。

一句话总结
**“采样随机性”是表面原因，而“浮点误差+并行非确定性+动态上下文+热更新”叠加在一起，才让『同一模型、同一提示』也逃不掉结果漂移。**

------

模型像“掷骰子”答题——
骰子本身带随机（采样），
桌子还老晃（浮点误差、并行算子、硬件波动），
所以同一问题每次点数都可能不一样。

------

补充，深度学习模型也总是出现同样的输入，返回结果不一致的问题，与上述结论的原因类似吗？

是“类似”，但“程度”不同。

1. 训练阶段
   深度学习模型（图像分类、目标检测…）也跑在 GPU 上，同样存在
   - 浮点累加顺序不同
   - cuDNN/ cuBLAS 选不同算法
     这些会让**同一张图、同一权重**算出的 logits 在小数点后 4~6 位有差异。
     不过，只要不用随机采样（softmax 后直接取 argmax），下游结果就是确定的；误差只在“Loss 小数点”里打转转，肉眼看不见。
2. 推断阶段
   如果模型最后一步要“随机”——
   - 生成任务：采样 token，温度>0 → 必随机
   - 检测/分割：NMS 里用随机种子做 tie-break → 可能随机
   - GAN/扩散模型：随机噪声 → 必随机
     这些就跟 LLM 一样，会出现“同图不同输出”。
     若全程 argmax、无随机算子，把 cudnn.benchmark=False、deterministic=True、固定 seed，就能做到 100 % 复现。

一句话大白话
“深度学习模型也会晃桌子（浮点误差），但只要最后不掷骰子（不采样），结果就稳；LLM 最后必须掷骰子，所以次次可能不一样。”



#### 综述- 训练推理和性能优化算法总结和实践

参考 ：[【万字长文】大模型训练推理和性能优化算法总结和实践](https://mp.weixin.qq.com/s/zUz5Y0DOFa2XL5AI_j34FA)

