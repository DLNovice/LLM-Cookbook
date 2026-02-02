前言：

- [PaddlePaddle深度学习基础](https://www.paddlepaddle.org.cn/documentation/docs/zh/guides/index_cn.html)
- [小土堆学习PyTorch](https://www.bilibili.com/video/BV1hE411t7RN)
- [沐神的PyTorch版《动手学习深度学习》系列](https://blog.csdn.net/qq_55535816/article/details/127466869)
- 跟着Yolo等项目学习深度学习框架实际是如何使用的

TODO：

- [Learn PyTorch for deep learning in a day Literally](https://www.bilibili.com/video/BV1kx4y1r79d)



但作为非算法工程师，这些也仅仅是了解了一些深度学习基础皮毛，似乎一直找不到将PyTorch利用起来的途径。



### TensorBoard

PyTorch 中主要通过以下方式使用 TensorBoard：

```
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter(log_dir="runs/exp1")

writer.add_scalar("train/loss", loss, step)
writer.add_scalar("train/lr", lr, step)
writer.add_text("config", str(args))

```

常见大模型 / NLP 框架几乎都支持 TensorBoard：

| 框架                | TensorBoard 支持 |
| ------------------- | ---------------- |
| HuggingFace Trainer | ✅ 默认支持       |
| PyTorch Lightning   | ✅ 强             |
| DeepSpeed           | ✅                |
| Fairseq             | ✅                |
| Megatron-LM         | ✅                |
| OpenNMT / ESPnet    | ✅                |

TensorBoard 在大模型 / NLP 训练中做什么？

- 监控训练是否“活着”：train loss / eval loss、perplexity、accuracy / BLEU / ROUGE等情况
- 学习率 & 调度器可视化（非常关键）
- 梯度 & 参数分布（调试利器）
- 大模型训练稳定性分析
- NLP 特有内容可视化
- 实验对比（多 run 同屏）