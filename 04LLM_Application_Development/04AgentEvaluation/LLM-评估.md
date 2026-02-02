好文分享：

- https://klu.ai/glossary/llm-evaluation
- https://www.51cto.com/article/785983.html
- https://developer.nvidia.com/zh-cn/blog/mastering-llm-techniques-evaluation/
- https://zhuanlan.zhihu.com/p/641416694

鉴于许多基于LLM的功能的新颖性和固有的不确定性，必须谨慎发布以维护隐私和社会责任标准。

LLM系统评估策略通常分为线上和线下两种。



# 评估指标

| Benchmarks          | Description                                                  | Reference URL                                                |
| ------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| GLUE Benchmark      | 通用语言理解评估。<br />GLUE (General Language Understanding Evaluation) benchmark provides a standardized set of diverse NLP tasks to evaluate the effectiveness of different language models | [https://gluebenchmark.com/](https://link.zhihu.com/?target=https%3A//gluebenchmark.com/) |
| SuperGLUE Benchmark | GLUE同一批人做的GLUE迭代升级版。<br />Compares more challenging and diverse tasks with GLUE, with comprehensive human baselines | [https://super.gluebenchmark.com/](https://link.zhihu.com/?target=https%3A//super.gluebenchmark.com/) |
| HellaSwag           | Evaluates how well an LLM can complete a sentence            | [https://rowanzellers.com/hellaswag/](https://link.zhihu.com/?target=https%3A//rowanzellers.com/hellaswag/) |
| TruthfulQA          | Measures truthfulness of model responses                     | [https://github.com/sylinrl/TruthfulQA](https://link.zhihu.com/?target=https%3A//github.com/sylinrl/TruthfulQA) |
| MMLU                | MMLU ((Massive Multitask Language Understanding) evaluates how well the LLM can multitask | https://github.com/hendrycks/test                            |



# 评估框架

许多框架是专门为LLM的评估而设计的。下面，我们重点介绍一些最广泛认可的。

| Frameworks / Platforms                 | Description                                                  | Tutorials/lessons | Reference |
| -------------------------------------- | ------------------------------------------------------------ | ----------------- | --------- |
| Azure AI Studio Evaluation (Microsoft) | Azure AI Studio是一个用于构建、评估和部署AGI以及自定义Copilots的一体化AI平台。<br />Azure AI Studio is an all-in-one AI platform for building, evaluating, and deploying generative AI solutions and custom copilots.Technical Landscape: No code: model catalog in AzureML studio & AI studio, Low-code: as CLI, Pro-code: as azureml-metrics SDK |                   |           |
| Prompt Flow (Microsoft)                | A suite of development tools designed to streamline the end-to-end development cycle of LLM-based AI applications, from ideation, prototyping, testing, and evaluation to production, deployment, and monitoring. |                   |           |
| Weights & Biases(Weights & Biases)     | A Machine Learning platform to quickly track experiments, version and iterate on datasets, evaluate model performance, reproduce models, visualize results and spot regressions, and share findings with colleagues. |                   |           |
| LangSmith (LangChain)                  | Helps the user trace and evaluate language model applications and intelligent agents to help user move from prototype to production. |                   |           |
| TruLens (TruEra)                       | TruLens provides a set of tools for developing and monitoring neural nets, including LLMs. This includes both tools for the evaluation of LLMs and LLM-based applications with TruLens-Eval and deep learning explainability with TruLens-Explain. |                   |           |
| Vertex AI Studio (Google)              | You can evaluate the performance of foundation models and your tuned generative AI models on Vertex AI. The models are evaluated using a set of metrics against an evaluation dataset that you provide. |                   |           |
| Amazon Bedrock                         | Amazon Bedrock supports model evaluation jobs. The results of a model evaluation job allow you to evaluate and compare a model's outputs, and then choose the model best suited for your downstream generative AI applications. Model evaluation jobs support common use cases for large language models (LLMs) such as text generation, text classification, question and answering, and text summarization. |                   |           |
| DeepEval (Confident AI)                | An open-source LLM evaluation framework for LLM applications. |                   |           |
| Parea AI                               | Parea helps AI Engineers build reliable, production-ready LLM applications. Parea provides tools for debugging, testing, evaluating, and monitoring LLM-powered applications. |                   |           |



# 数据集

TODO