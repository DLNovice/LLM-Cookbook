> 参考：[qwen3-embedidng、qwen3-reranker模型解读 使用ray进行部署](https://www.bilibili.com/video/BV18FThzuE4b)

主要概述了两部分内容：

- 结合推理源码，调试了一遍qwen3的embedding模型和reranker模型的推理过程
- 面向在显卡上部署多份一样的模型的问题，提出基于ray的部署方案