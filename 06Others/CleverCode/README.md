# 焚诀

日常工具：

- 论文阅读：心流AI、秘塔AI、NotebookLM



## paper-reading

> Gem 管理器 + system prompt + gemini pro + canvas

参考视频：https://www.bilibili.com/video/BV1FqebznEWU

也就是在Gemini的“[探索Gem](https://gemini.google.com/gems/view)”栏，自定义一个自己的Gem，预先定义好SystemPrompt，然后打开canvas模式，就可以批量阅读论文了。

示例Prompt：

```
你是一位顶级的 AI researcher 以及全栈开发者，同时也是一位精通学术内容解读与数据可视化的信息设计师。你的任务是将一篇复杂的学术论文，转化为一个符合苹果官网设计美学、交互流畅、信息层级分明的动态HTML网页。

请将以下指定的学术论文，严格按照要求，生成一个单一、完整的`index.html`文件。网页需深度解析并重点展示论文的
- **研究动机**：发现了什么问题，为什么需要解决这个问题，本文研究的 significance 是什么
- **数学表示及建模**：从符号/表示到公式，以及公式推导和算法流程，注意支持 latex 的渲染
- **实验方法与实验设计**：系统性整理实验细节（比如模型、数据、超参数、prompt等），尽可能参考 appendix，达到可复现的程度；
- **实验结果及核心结论**：对比了那些baseline，达到了什么效果，揭示了什么结论和insights
- **你的评论**：作为一个犀利的reviewer，整体锐评下这篇工作，优势与不足，以及可能的改进方向
- **One More Thing**: 你也可以自由发挥本文中其他你认为重要、希望分享给我的内容

注意：
1. 整个网页所有的符号及公式，都要能支持 latex 渲染（不只是公式块，还包括inline的公式，注意**行内公式不要换行**）；
2. 除公式以及一些核心术语和技术名词外，尽可能用中文。
3. figure/table 插入时，用论文中具体的 figure/table 来表示。特别的，对于图片，如果无法直接放到网页中，就使用占位符表示，方便检索；对于表格，如果是关键实验相关表格 则按照latex格式进行渲染，将表格内具体内容放到网页中。
4. 要尽可能地事无巨细，目标是读完这个网页，基本把握了论文90%的内容了，可以达到复现论文的程度。

在输出最终代码前，请暂停并进行一次彻底的自我校正。确保你的 `index.html` 文件严格遵守以下所有规则：它必须是单一、完整的，并完美融合了苹果的设计美学。仔细检查每一个 LaTeX 公式，都能被准确地渲染出来，特别是行内公式，确保它们无缝嵌入文本中，绝不换行。内容的深度必须足以支撑起论文90%的核心信息和复现所需的所有关键细节（特别是实验部分）。最后，以一个顶尖研究者的身份，给出一份真正犀利、有洞见的评述。
```





## scientific-illustration

>科研绘图（teaser/poster），nano banana vs. GPT，nature/science 美学风格

参考视频：https://www.bilibili.com/video/BV12dHvz7Eb8

参考笔记：[科研绘图.ipynb](https://github.com/chunhuizhang/prompts_for_academic/blob/main/leverage/%E7%A7%91%E7%A0%94%E7%BB%98%E5%9B%BE.ipynb)

主要是评测了下目前模型进行科研绘图的能力，虽然还不能完美的端到端，但是效果已经很惊喜。



# 写好代码

> 微信读书

《软技能：代码之外的生存指南》、《代码整洁之道》、《程序员的底层思维》等等



> 参考：[一位工程师对“好代码”的 7 年思考](https://mp.weixin.qq.com/s/X4VOP7pAxRYzO6mRsD9ecw?scene=1&click_id=10)

TODO



> 参考：[章老师说 - 在大模型时代对软件工程能力的反思](https://mp.weixin.qq.com/s/cXrWF3aI4M8OwT8WHu1cqg)

TODO



# 思想对齐

> 参考：[字节公布人才观，一次披露招人用人底层逻辑](https://mp.weixin.qq.com/s/rpziB-8sRVlaRHWIdGuSEQ)

具体包括：

1. 和优秀的人，做有挑战的事
2. 用人看本质，看潜力不看资历
3. 敢招比自己强的人
4. 为最优秀的人提供最好的回报
5. 激励拉开区分度，不吃大锅饭
6. 以能定级、以级定薪、以绩定奖



> 参考：[分享《一人企业方法论》](https://mp.weixin.qq.com/s/A7XaUkYIufpdE0Uu1JUK5Q)

喜剧演员威尔.罗杰斯说过：“学习只有两种途径：一个是阅读，另一个是与更聪明的人为伍。”



> 参考：八年算法之路-挺逗的汪

大佬原文：

- [第一章：初出茅庐，春风得意马蹄疾！](https://www.xiaohongshu.com/discovery/item/6725e70e000000001a01f596?source=webshare&xhsshare=pc_web&xsec_token=ABIsadks1MFbjHSWytDm5ls5FePn0b3VBDWjsW5mNqVjs=&xsec_source=pc_share)
- [第二章：风云已起，内斗频生！](https://www.xiaohongshu.com/discovery/item/6727627a000000001901bc82?source=webshare&xhsshare=pc_web&xsec_token=ABAZ73fm7k3PFvHO_w64Lcg0zYiTi-LLzjepMGPPEmsgk=&xsec_source=pc_share)
- [第三章：作茧自缚，报应不爽！](https://www.xiaohongshu.com/discovery/item/672af2de000000001a01c2b7?source=webshare&xhsshare=pc_web&xsec_token=ABkHw1MlrW-3tKsOwiqHvrWe8V0TwitHIWMDt77d0rsmU=&xsec_source=pc_share)
- [第四章：涅槃重生，否极泰来](https://www.xiaohongshu.com/discovery/item/673562f10000000019017620?source=webshare&xhsshare=pc_web&xsec_token=ABIVAo89YmT32Xj1QXjUahe4i2Mc1HegOmHsUa1QQAQeQ=&xsec_source=pc_share)

五年兼职创业路：

- [第一章：一腔热血撞上空手套白狼](https://www.xiaohongshu.com/discovery/item/6741ac3d00000000080053d4?source=webshare&xhsshare=pc_web&xsec_token=AB7Arwm2wbpgo_gyFJ6PWRvbgF8BQbd1yMXV1rmMyPvQw=&xsec_source=pc_share)

外传：其他岗位

- [风控最好别选？tob  or toc？对内业务 or 对外业务？](https://www.xiaohongshu.com/discovery/item/671c921b00000000210095bf?source=webshare&xhsshare=pc_web&xsec_token=ABboRTFXakH_KkNLhGlIiaI5BptOZNadXPTMGnpTlV6wQ=&xsec_source=pc_share)
- [为什么我建议大家有好的选择就别接中台offer？](https://www.xiaohongshu.com/discovery/item/67490f38000000000703279d?source=webshare&xhsshare=pc_web&xsec_token=ABEonTCwo3CvXY5VuG8Oq9TgrEY63ZIkCnKQov4RR1AU0=&xsec_source=pc_share)
- [运营岗位有哪些、都干啥？ 也分三六九等？](https://www.xiaohongshu.com/discovery/item/673954d2000000001a01d612?source=webshare&xhsshare=pc_web&xsec_token=ABncO5Kl4fnGnLk1yW-DLtF1FoCCAHKMtB61GKtukAPL4=&xsec_source=pc_share)
- [数据开发难度大吗？卷吗？发展前景咋样？](https://www.xiaohongshu.com/discovery/item/677bc220000000000900f22f?source=webshare&xhsshare=pc_web&xsec_token=ABJbs0ckv2CyB_eL7faR9OyroMciUgAlYvGMA8W7Fez4M=&xsec_source=pc_share)



# 其他

### 八股与项目

为什么 研发序列比产品等序列在职时间要更长很多？

什么是序列：

- 在互联网和科技公司中，“序列”（或“职级序列”）是对具有相似工作职能和职业发展路径的一组岗位的分类。
- 研发序列（R&D/技术序列）代表岗位： 软件工程师（前端、后端、客户端）、算法工程师、测试开发工程师、数据工程师等。
- 产品序列（产品/运营序列）代表岗位： 产品经理（PM）、产品运营、用户运营、数据分析师（有时归入运营或业务序列）等。

造成在职时间差异的几个主要原因：

-  技能积累的壁垒与沉没成本高：
  - 研发：技能越老越值钱（Deep Skill）
  - 产品：技能更依赖“网感”和趋势（Soft Skill）
-  职业发展的路径差异
  - 研发序列：有清晰且长期的专业通道
  - 产品序列：晋升通道相对更窄
- 市场风险与机会的驱动
  - 产品序列对“风口”更敏感
  - 研发序列的通用性更强

换个角度，研发与产品：

- 研发：准备各种八股/基础知识
- 产品：讲自己的项目

如果研发也是只讲项目，那么在职时间也会大大缩短。



### 一人公司

参考：[一人公司第一步（路线一20分钟掌握）- 系列](https://www.bilibili.com/video/BV1SKU6BnERr)