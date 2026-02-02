Transformer相关解读：

- 大佬博客：
  - [一文彻底搞懂 Transformer（图解+代码手撕）](https://zhuanlan.zhihu.com/p/694373104)
  - [【手撕Transformer】](https://blog.csdn.net/wl1780852311/article/details/121033915)
  - [手撕Transformer！](https://blog.csdn.net/xiaoh_7/article/details/140019530)
- 视频教程：
  - [沐神 - Transformer论文逐段精读【论文精读】](https://www.bilibili.com/video/BV1pu411o7BE)
  - [飞天闪客 - 硬读 Transformer 经典论文！](https://www.bilibili.com/video/BV1k4o7YqEEi)
  - [论文解读及Transformer架构详细介绍](https://www.bilibili.com/video/BV1xoJwzDESD)
- 其他：
  - [纯手工绘制 Transformer 架构图](https://github.com/An-Jhon/Hand-Drawn-Transformer/tree/main)






> 参考：[小白debug - Transformer是什么？](https://www.bilibili.com/video/BV1G4iMBeEWH)

动画做的很容易理解：

- token 与向量是什么 
- embedding是什么 
- Q、K、V 是什么 
- 注意力机制是什么 
- Attention是什么 
- 为什么说Attention is all you need 
- 计算机怎么处理翻译问题 
- 多头注意力是什么 
- Add & Norm 是什么 
- 残差网络和归一化是什么 
- 前馈网络FFN是什么 
- 编码层、编码器是什么 
- 解码层、解码器是什么 
- Transformer是什么



# Transformer源码学习项目

这是一个完整的Transformer模型实现项目，基于论文《Attention Is All You Need》(Vaswani et al., 2017)。项目从零开始实现了Transformer的所有核心组件，并提供了详细的代码注释和可视化分析。

## 📚 项目概述

本项目旨在帮助学习者深入理解Transformer架构的内部工作原理。通过逐步实现每个组件，您可以清晰地了解Transformer是如何构建的，以及各个部分如何协同工作。

### 项目特色

- **从零实现**: 不依赖高级API，完全手动实现所有组件
- **详细注释**: 每行代码都有中文注释，解释其作用和原理
- **原论文对照**: 代码中标注了与论文公式的对应关系
- **可视化分析**: 提供多种可视化工具帮助理解
- **完整训练**: 包含模型训练和推理的完整流程
- **性能对比**: 与PyTorch官方实现进行对比

## 🏗️ 项目结构

项目包含6个Jupyter Notebook文件，按Transformer架构的构建顺序组织：

### 1. 01embedding.ipynb - 嵌入层实现
- **TokenEmbedding**: 词嵌入层
- **PositionalEncoding**: 位置编码（基于论文公式）
- **TransformerEmbedding**: 完整的嵌入层组合
- **可视化**: 位置编码的可视化分析
- **测试**: 与PyTorch官方实现的对比

### 2. 02attention.ipynb - 注意力机制
- **Scaled Dot-Product Attention**: 缩放点积注意力
- **Multi-Head Attention**: 多头注意力机制
- **掩码机制**: Padding Mask和Look-ahead Mask
- **注意力权重可视化**: 理解注意力如何工作
- **数学原理**: 详细的公式推导和解释

### 3. 03layernorm.ipynb - 层归一化
- **SimpleLayerNorm**: 层归一化实现
- **数学原理**: LayerNorm的公式和作用
- **与BatchNorm对比**: 理解两者的区别
- **可视化分析**: 层归一化的效果展示
- **性能测试**: 不同配置的对比实验

### 4. 04encoder.ipynb - 编码器
- **EncoderLayer**: 单个编码器层
- **Encoder**: 完整编码器
- **子层结构**: 自注意力 + 前馈网络 + 残差连接
- **注意力分析**: 编码器注意力权重可视化
- **性能测试**: 编码器的前向传播测试

### 5. 05decoder.ipynb - 解码器
- **DecoderLayer**: 单个解码器层
- **Decoder**: 完整解码器
- **掩码自注意力**: 防止信息泄露
- **编码器-解码器注意力**: 跨注意力机制
- **自回归生成**: 逐步生成序列

### 6. 06complete_transformer.ipynb - 完整模型
- **完整Transformer**: 整合所有组件
- **训练流程**: 完整的训练循环
- **推理功能**: 序列到序列的翻译
- **性能分析**: 模型参数和推理速度分析
- **对比分析**: 与PyTorch官方实现的对比

## 🚀 快速开始

### 环境要求

```bash
pip install torch numpy matplotlib jupyter
```

### 学习顺序

建议按照以下顺序学习：

1. **从嵌入层开始** (01embedding.ipynb)
   - 理解词嵌入和位置编码的概念
   - 掌握如何将离散的词转换为连续的向量表示

2. **学习注意力机制** (02attention.ipynb)
   - 深入理解注意力机制的工作原理
   - 学习掩码的作用和实现

3. **掌握层归一化** (03layernorm.ipynb)
   - 理解层归一化的数学原理
   - 对比不同的归一化方法

4. **构建编码器** (04encoder.ipynb)
   - 理解编码器的结构和作用
   - 学习如何处理输入序列

5. **构建解码器** (05decoder.ipynb)
   - 理解解码器的自回归特性
   - 掌握跨注意力机制

6. **整合完整模型** (06complete_transformer.ipynb)
   - 训练完整的Transformer模型
   - 进行序列到序列的翻译任务


