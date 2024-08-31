# 常用变量和函数
# 同济子豪兄 2024-8-31

print('导入工具包')
from transformers import AutoConfig, AutoTokenizer
from optimum.intel.openvino import OVModelForCausalLM

llm_model_path = "model/Phi-3.5-mini-instruct-ov-int4"

ov_config = {"PERFORMANCE_HINT": "LATENCY", "NUM_STREAMS": "1", "CACHE_DIR": ""}

print('开始载入phi3.5-mini-instruct-openvino-int4模型')
ov_model = OVModelForCausalLM.from_pretrained(
    llm_model_path,
    device='GPU',
    ov_config=ov_config,
    config=AutoConfig.from_pretrained("model/Phi-3.5-mini-instruct-ov-int4/"),
    trust_remote_code=True,
)
print('模型成功载入')

tok = AutoTokenizer.from_pretrained(llm_model_path, trust_remote_code=True)
tokenizer_kwargs =  {"add_special_tokens": False}

def phi35_ask(question="你了解 .NET 吗?"):
    prompt = "<|user|>\n{}\n<|end|><|assistant|>\n".format(question)
    input_tokens = tok(prompt, return_tensors="pt", **tokenizer_kwargs)
    answer = ov_model.generate(**input_tokens, max_new_tokens=1024)
    result = tok.batch_decode(answer, skip_special_tokens=True)[0]
    # result = result.split('\n')[1:][0].strip()
    return result