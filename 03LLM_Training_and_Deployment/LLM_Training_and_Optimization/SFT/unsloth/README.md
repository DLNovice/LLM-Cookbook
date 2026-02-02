### 概述

参考unsloth的微调流程：

-  [Fine-tuning LLMs Guide](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide#id-1.-understand-fine-tuning)：概述了微调的全流程，不过每个模块对应的源码需要阅读对应的子模块，并结合一些完整案例，才能拼凑出理想的、完整的微调代码
-  [Datasets Guide](https://docs.unsloth.ai/basics/datasets-guide#synthetic-data-generation)

示例教程：

- https://juejin.cn/post/7498300880053026843
- https://www.cnblogs.com/shanren/p/18251730
- https://zhuanlan.zhihu.com/p/31437081152
- https://www.5bei.cn/unsloth-tutorial-how-to-fine-tune-llama-3-and-expo.html#6Alpaca_shu_ju_ji

实践参考：

- [unsloth - qwen3微调](https://docs.unsloth.ai/basics/qwen3-how-to-run-and-fine-tune#fine-tuning-qwen3-with-unsloth)
- [unsloth - gpt-oss微调](https://docs.unsloth.ai/basics/gpt-oss-how-to-run-and-fine-tune/tutorial-how-to-fine-tune-gpt-oss#local-gpt-oss-fine-tuning)



### 快速上手

#### 环境准备

基于vllm提供模型服务：

```
pip install "vllm>=0.8.5"
pip install -U huggingface_hub
echo 'export HF_ENDPOINT=https://hf-mirror.com' >> ~/.bashrc
source ~/.bashrc

huggingface-cli download --resume-download Qwen/Qwen3-30B-A3B-Instruct-2507 --local-dir Qwen/Qwen3-30B-A3B-Instruct-2507

python -m vllm.entrypoints.openai.api_server --host 0.0.0.0 --port 8007 --max-model-len 8000 --model Qwen/Qwen3-30B-A3B-Instruct-2507 --disable-log-requests --swap-space 16 --tensor-parallel-size 2 --gpu-memory-utilization 0.9

curl --location 'http://0.0.0.0:8007/v1/chat/completions' \
  --header 'Content-Type: application/json' \
  --data '{
  "model": "Qwen/Qwen3-30B-A3B-Instruct-2507",
  "messages": [
    {
      "role": "user",
      "content": "简单解释一下量子计算"
    }
  ],
  "temperature": 0.2,
  "stream": true
}'
```



#### 数据准备

原始数据准备：

```
git clone https://github.com/CloudPSS/docs.git
```

Unsloth 框架通常使用标准的 Hugging Face `Dataset` 格式。对于指令微调（Instruction-Tuning），最常用的格式是包含 `instruction`（指令）、`input`（输入）和 `output`（输出）字段。

遍历原始数据中的markdown文档，并转换为标准数据集，参考代码：

```
import os
import json
import tiktoken
import asyncio
from openai import AsyncOpenAI  # 使用 AsyncOpenAI 客户端
from tqdm.asyncio import tqdm  # 使用异步版本的 tqdm


# 初始化异步 OpenAI 客户端
client = AsyncOpenAI(
    base_url="http://localhost:8007/v1",  # vLLM API 地址
    api_key="EMPTY"                       # vLLM 默认不校验 key，可以随便填
)

# 配置参数
INPUT_FOLDER = "/home/user/WorkSpace/Learn/LLM/TrainLLM/learn_unsloth/dataset/docs"  # 你的Markdown文档所在的主文件夹
OUTPUT_JSONL = "domain_knowledge_dataset2.jsonl"
TOKEN_CHUNK_SIZE = 2048  # 每个文本块的token数量
LLM_MODEL = "Qwen/Qwen3-30B-A3B-Instruct-2507"  # 推荐使用 GPT-4 或更强大的模型以获得更高质量的结果
MAX_CONCURRENT_REQUESTS = 10

# 用于计算 token
encoding = tiktoken.get_encoding("cl100k_base")

def get_text_chunks(text, max_tokens):
    """
    将长文本分割成固定 token 大小的块。
    """
    tokens = encoding.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
    return chunks

async def generate_qa_pair(chunk, model, sem):
    """
    使用异步方式调用 LLM 服务，为文本块生成问答对。
    """
    prompt = f"""
    你是一个数据标注专家，专门从文档中创建高质量的问答数据集。
    请根据以下提供的**文本片段**，提取1到3个核心知识点，并为每个知识点生成一个简洁、准确的问答对。
    问答对必须包含“instruction”（指令）、“input”（包含问题的核心上下文）和“output”（精确的响应）。
    请确保你的响应只包含一个合法的 JSON 数组，每个对象代表一个问答对。

    文本片段：
    ---
    {chunk}
    ---

    请返回如下格式的 JSON 数组：
    [
      {{
        "instruction": "...",
        "input": "...",
        "output": "..."
      }}
    ]
    """
    
    async with sem:
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个严谨的数据标注助手，只返回JSON格式的数据。"},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            
            # 尝试加载 JSON
            qa_pairs = json.loads(content)
            
            # 修复核心逻辑：如果返回的是单个对象，将其包装在列表中
            if isinstance(qa_pairs, dict):
                qa_pairs = [qa_pairs]
                
            if not isinstance(qa_pairs, list):
                print(f"警告: LLM 返回的不是列表格式或字典，内容为: {content[:100]}...")
                return []
            
            # 过滤掉不完整的对象
            valid_pairs = []
            for pair in qa_pairs:
                if isinstance(pair, dict) and 'instruction' in pair and 'input' in pair and 'output' in pair:
                    valid_pairs.append(pair)
                else:
                    print(f"警告: 发现不完整的 JSON 对象，内容为: {pair}")

            return valid_pairs
            
        except json.JSONDecodeError as e:
            print(f"警告: LLM 返回的 JSON 格式不正确，跳过此块。错误: {e}, 内容: {content[:100]}...")
            return []
        except Exception as e:
            print(f"发生错误: {e}")
            return []

async def process_file(file_path, sem):
    """
    处理单个 Markdown 文件，并异步生成所有问答对。
    """
    all_qa_pairs = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        chunks = get_text_chunks(markdown_content, TOKEN_CHUNK_SIZE)
        tasks = [generate_qa_pair(chunk, LLM_MODEL, sem) for chunk in chunks]
        
        results = await tqdm.gather(*tasks, desc=f"处理文件: {os.path.basename(file_path)}", leave=False)
        
        for qa_pairs in results:
            all_qa_pairs.extend(qa_pairs)
            
        return all_qa_pairs
    except Exception as e:
        print(f"处理文件 {file_path} 时发生错误: {e}")
        return []

async def main(root_folder, output_file):
    """
    主异步函数，遍历所有文件并并发处理。
    """
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    file_paths = []
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith(".md"):
                file_paths.append(os.path.join(dirpath, filename))
    
    print(f"找到 {len(file_paths)} 个 Markdown 文件，开始异步处理...")
    
    tasks = [process_file(file_path, semaphore) for file_path in file_paths]
    all_data_lists = await tqdm.gather(*tasks, desc="总进度")

    total_qa_pairs = 0
    with open(output_file, 'w', encoding='utf-8') as f:
        for qa_pair_list in all_data_lists:
            for qa_pair in qa_pair_list:
                f.write(json.dumps(qa_pair, ensure_ascii=False) + '\n')
                total_qa_pairs += 1
            
    print(f"\n数据集生成完毕，共包含 {total_qa_pairs} 条问答数据。")
    print(f"数据集已成功保存到 {output_file}")


if __name__ == "__main__":
    if not os.path.exists(INPUT_FOLDER):
        print(f"错误：输入文件夹 '{INPUT_FOLDER}' 不存在。请创建该文件夹并放入 Markdown 文件。")
    else:
        asyncio.run(main(INPUT_FOLDER, OUTPUT_JSONL))
```

最终生成的jsonl示例：

```
{"instruction": "请根据提供的文本片段，提取关于 CloudPSS 知识库的核心知识点，并生成相应的问答对。", "input": "CloudPSS 知识库的目标是构建一个开源、开放、协作、共享的生态。其文档系统支持通过 GitHub 进行版本管理，并提供最新版和预发布版本的链接。", "output": "CloudPSS 知识库的目标是构建一个开源、开放、协作、共享的生态。"}
{"instruction": "请说明 CloudPSS 的起源及其最初指代的平台。", "input": "CloudPSS 最早发布于 2016 年 9 月 21 日，最初仅指代团队自主研发的电磁暂态云仿真平台。", "output": "CloudPSS 最初指代的是团队自主研发的电磁暂态云仿真平台，即 CloudPSS EMTLab (RT)，于 2016 年 9 月 21 日发布。"}
{"instruction": "根据更新日志，描述 XStudio v4.3 版本中颜色选择控件新增的功能。", "input": "XStudio 更新至 v4.3 版本，颜色选择控件新增了哪些功能？", "output": "颜色选择控件支持透明度设置，并添加了取色器功能。"}
```

当然，也可以把jsonl转为json标准格式

```
import json

def jsonl_to_json_array(input_file, output_file):
    """
    将 JSONL 文件转换为一个包含所有 JSON 对象的 JSON 数组。
    """
    data = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:  # 忽略空行
                    try:
                        obj = json.loads(line)
                        data.append(obj)
                    except json.JSONDecodeError as e:
                        print(f"警告：跳过格式不正确的行：{line[:50]}... 错误：{e}")
    except FileNotFoundError:
        print(f"错误：输入文件 '{input_file}' 未找到。")
        return

    print(f"从 '{input_file}' 中读取了 {len(data)} 条数据。")

    with open(output_file, 'w', encoding='utf-8') as f:
        # 使用 json.dump 来写入完整的 JSON 数组
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"数据已成功转换为 JSON 数组并保存到 '{output_file}'。")

# --- 使用方法 ---
if __name__ == "__main__":
    # 请将这里的'input_dataset.jsonl'替换为你生成的文件名
    INPUT_FILE = "domain_knowledge_dataset.jsonl"
    OUTPUT_FILE = "dataset_as_json_array.json"

    jsonl_to_json_array(INPUT_FILE, OUTPUT_FILE)
```

示例结果：

```
[
  {"instruction": "...", "input": "...", "output": "..."},
  {"instruction": "...", "input": "...", "output": "..."},
  {"instruction": "...", "input": "...", "output": "..."}
]
```

不过 LLM 微调所需的 JSONL 格式，没必要转换。



#### 开始训练

参考：

- [unsloth - qwen3微调](https://docs.unsloth.ai/basics/qwen3-how-to-run-and-fine-tune#fine-tuning-qwen3-with-unsloth)
- [unsloth - gpt-oss微调](https://docs.unsloth.ai/basics/gpt-oss-how-to-run-and-fine-tune/tutorial-how-to-fine-tune-gpt-oss#local-gpt-oss-fine-tuning)

环境准备：

```
uv pip install unsloth vllm
```

示例代码：以unsloth为例

```
from unsloth import FastLanguageModel
import torch
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig # Import SFTTrainer and SFTConfig
from transformers import TextStreamer

# Define model parameters
max_seq_length = 1024
dtype = None

# Load the Unsloth model and tokenizer
model_name = "unsloth/Llama-3.2-3B-Instruct-bnb-4bit"
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=model_name,
    dtype=dtype,
    max_seq_length=max_seq_length,
    load_in_4bit=True,
    full_finetuning=False,
)

# Apply PEFT for LoRA fine-tuning
model = FastLanguageModel.get_peft_model(
    model,
    r=8,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj",],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
    use_rslora=False,
    loftq_config=None,
)

# Define the path to your dataset and load it
DATASET_FILE = "/home/user/WorkSpace/Learn/LLM/TrainLLM/learn_unsloth/dataset/domain_knowledge_dataset.jsonl"
print("加载数据集...")
dataset = load_dataset("json", data_files=DATASET_FILE, split="train")

# Define the prompt template for formatting
prompt_template = """### Instruction:
{instruction}

### Input:
{input}

### Response:
{output}"""

# Define the formatting function to prepare the dataset for fine-tuning
def formatting_prompts_func(examples):
    instructions = examples["instruction"]
    inputs       = examples["input"]
    outputs      = examples["output"]
    texts = []
    for instruction, input_text, output_text in zip(instructions, inputs, outputs):
        text = prompt_template.format(
            instruction=instruction,
            input=input_text,
            output=output_text
        )
        texts.append(text)
    return { "text" : texts }

# Map the formatting function to the dataset
print("格式化数据集...")
dataset = dataset.map(formatting_prompts_func, batched=True)

# Define the directory to save the output model
OUTPUT_MODEL_DIR = "/home/user/WorkSpace/Learn/LLM/TrainLLM/learn_unsloth/lora_adapter_model"

# Use SFTTrainer from TRL, which is optimized for this task
print("初始化 SFTTrainer...")
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text", # Tell SFTTrainer to use the "text" column
    max_seq_length = max_seq_length,
    dataset_num_proc = 2, # Process dataset in parallel
    packing = False, # No packing
    args = SFTConfig(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        num_train_epochs = 3,
        learning_rate = 2e-4,
        logging_steps = 10,
        report_to = "none",  # tensorboard, wandb
        save_steps = 500,
        save_total_limit = 3,
        output_dir = OUTPUT_MODEL_DIR,
    ),
)

# Start training the model
print("开始训练...")
trainer.train()

# Test the fine-tuned model with a new prompt
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "请说明 CloudPSS 的起源及其最初指代的平台。"},
]

inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    return_tensors="pt",
    return_dict=True,
).to(model.device)

print("生成回答...")
streamer = TextStreamer(tokenizer, skip_prompt=True)
_ = model.generate(**inputs, max_new_tokens=2048, streamer=streamer)

# Save the final fine-tuned model
save_directory = "/home/user/WorkSpace/Learn/LLM/TrainLLM/learn_unsloth/sft_model"
model.save_pretrained_merged(save_directory, tokenizer, save_method='forced_merged_4bit')

print("训练和保存完成。")

```

示例输出：

```
Unsloth 2025.9.1 patched 28 layers with 28 QKV layers, 28 O layers and 28 MLP layers.
加载数据集...
格式化数据集...
初始化 SFTTrainer...
开始训练...
==((====))==  Unsloth - 2x faster free finetuning | Num GPUs used = 1
   \\   /|    Num examples = 2,227 | Num Epochs = 3 | Total steps = 420
O^O/ \_/ \    Batch size per device = 4 | Gradient accumulation steps = 4
\        /    Data Parallel GPUs = 1 | Total batch size (4 x 4 x 1) = 16
 "-____-"     Trainable parameters = 12,156,928 of 3,224,906,752 (0.38% trained)
  0%|                                                              | 0/420 [00:00<?, ?it/s]Unsloth: Will smartly offload gradients to save VRAM!
  
{'loss': 2.5393, 'grad_norm': 0.8621740341186523, 'learning_rate': 0.00019807228915662652, 'epoch': 0.07}
.....
{'loss': 0.846, 'grad_norm': 3.4532642364501953, 'learning_rate': 4.819277108433736e-07, 'epoch': 3.0}

{'train_runtime': 546.0727, 'train_samples_per_second': 12.235, 'train_steps_per_second': 0.769, 'train_loss': 1.194579553604126, 'epoch': 3.0}
100%|████████████████████████████████████████████████████| 420/420 [09:06<00:00,  1.30s/it]
生成回答...
CloudPSS 是一个用于表示 CloudPSS 平台的标签，其起源于 CloudPSS 元件，用于指代 CloudPSS 平台中的元件组件。<|eot_id|>
Detected local model directory: /home/user/.cache/modelscope/hub/models/unsloth/llama-3___2-3b-instruct-bnb-4bit
Unsloth: Merging LoRA weights into 4bit model...
/home/user/WorkSpace/Learn/LLM/TrainLLM/learn_unsloth/.venv/lib/python3.12/site-packages/peft/tuners/lora/bnb.py:348: UserWarning: Merge lora module to 4-bit linear may get different generations due to rounding errors.
  warnings.warn(
Unsloth: Merging finished.
Unsloth: Found skipped modules: ['lm_head']. Updating config.
Unsloth: Saving merged 4bit model to /home/user/WorkSpace/Learn/LLM/TrainLLM/learn_unsloth/sft_model...
Unsloth: Merged 4bit model saved.
Unsloth: Merged 4bit model process completed.
训练和保存完成。
```

