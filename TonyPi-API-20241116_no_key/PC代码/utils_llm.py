# 调用大模型 API
# 同济子豪兄 2024-11-16，写于29岁生日

import os
from API_KEY import *
from robot_prompt import robot_order_template

def load_qwen_ov():
    import openvino_genai as ov_genai
    # 载入OpenVINO IR格式的大模型
    print('载入OpenVINO IR格式大模型')
    device = 'GPU'
    pipe = ov_genai.LLMPipeline("Qwen2-7B-Instruct-int4-ov", device)
    print('Qwen2-7B-Instruct模型载入完成')
    return pipe

# 函数：智能体Agent编排动作
# AIPC 本地 OpenVINO 部署 Qwen开源大模型
def agent_plan_qwen_ov(pipe, question="先鞠个躬，再打个招呼，蹲下，最后站起来"):
    prompt_human = robot_order_template + question
    prompt_machine = "<|im_start|>system\n<|im_end|>\n<|im_start|>user\n{}<|im_end|>\n<|im_start|>assistant\n".format(prompt_human)
    result = pipe.generate(prompt_machine)
    action_plan_json = eval(result.texts[0])
    print('【大模型输出】\n', action_plan_json)

    # 获取动作编排
    agent_plan_list = action_plan_json['action']
    agent_plan_str = str(agent_plan_list)
    # print('【智能体Agent编排动作列表】\n', agent_plan_list)
    
    # 获取AI回复
    ai_response = action_plan_json['response']
    # print('【AI回复】\n', ai_response)

    # 写入txt文件
    with open('temp/agent_plan.txt', 'w') as f:
        f.write(agent_plan_str)

    # 把动作编排txt文件传到开发板
    terminal = 'scp temp/agent_plan.txt pi@{}:~/TonyPi/OpenVINO/temp/'.format(PI_IP)
    os.system(terminal)
        
    return agent_plan_list, ai_response

# 函数：智能体Agent编排动作
# 百度千帆大模型平台
import qianfan
# 传入 ACCESS_KEY 和 SECRET_KEY
os.environ["QIANFAN_ACCESS_KEY"] = QIANFAN_ACCESS_KEY
os.environ["QIANFAN_SECRET_KEY"] = QIANFAN_SECRET_KEY
# 选择大语言模型
MODEL = "ERNIE-Bot-4"
# MODEL = "ERNIE Speed"
# MODEL = "ERNIE-Lite-8K"
# MODEL = 'ERNIE-Tiny-8K'
chat_comp = qianfan.ChatCompletion(model=MODEL)
def agent_plan_qianfan(question="先鞠个躬，再打个招呼，蹲下，最后站起来"):
    '''
    百度智能云千帆大模型平台API
    '''    
    # 构建完整提示词
    PROMPT = robot_order_template + question
    
    # 输入给大模型
    resp = chat_comp.do(
        messages=[{"role": "user", "content": PROMPT}], 
        top_p=0.8, 
        temperature=0.3, 
        penalty_score=1.0
    )
    
    result = resp["result"]

    action_plan_json = eval(result[result.find('{'):result.find('}')+1])
    
    print('【大模型输出】\n', action_plan_json)

    # 获取动作编排
    agent_plan_list = action_plan_json['action']
    # print('【智能体Agent编排动作列表】\n', agent_plan_list)
    # 获取AI回复
    ai_response = action_plan_json['response']
    # print('【AI回复】\n', ai_response)
    
    return agent_plan_list, ai_response

# 函数：智能体Agent编排动作
# 零一万物：单轮对话
import openai
from openai import OpenAI
def agent_plan_yi(question="先鞠个躬，再打个招呼，蹲下，最后站起来"):
    
    # 选择大模型
    MODEL = 'yi-large'
    # MODEL = 'yi-medium'
    # MODEL = 'yi-spark'
    
    client = OpenAI(
        api_key=YI_KEY,
        base_url='https://api.lingyiwanwu.com/v1'
    )
    
    # 调用大模型API
    PROMPT = robot_order_template + question
    MESSAGES = [{'role': 'user', 'content': PROMPT}]
    completion = client.chat.completions.create(
        model=MODEL,
        messages=MESSAGES
    )
    
    # 解析大模型回复
    result = completion.choices[0].message.content.strip()
    action_plan_json = eval(result)
    print('【大模型输出】\n', action_plan_json)
    # 获取动作编排
    agent_plan_list = action_plan_json['action']
    # 获取AI回复
    ai_response = action_plan_json['response']
        
    return agent_plan_list, ai_response

# 函数：智能体Agent编排动作
# 零一万物-带多轮对话历史记录的对话
MESSAGES_HISTORY = [
    {'role': 'user', 'content': robot_order_template},
    {'role': 'assistant', 'content': '好的，请你说出指令吧'}
]
def agent_plan_yi_history(question="先鞠个躬，再打个招呼，蹲下，最后站起来"):
    
    # 选择大模型
    MODEL = 'yi-large'
    # MODEL = 'yi-medium'
    # MODEL = 'yi-spark'
    
    client = OpenAI(
        api_key=YI_KEY,
        base_url='https://api.lingyiwanwu.com/v1'
    )
    
    # 调用大模型API
    MESSAGES_HISTORY.append({'role': 'user', 'content': question}) # 添加多轮对话历史记录
    
    completion = client.chat.completions.create(
        model=MODEL,
        messages=MESSAGES_HISTORY
    )
    
    # 解析大模型回复
    result = completion.choices[0].message.content.strip()
    # print('模型API回复', result)
    if result[:7] == "```json": # 模型API回复以```json开头
        result = result[7:-3]
    MESSAGES_HISTORY.append({'role': 'assistant', 'content': result}) # 添加多轮对话历史记录
    # print('多轮对话历史记录', MESSAGES_HISTORY)
    
    action_plan_json = eval(result)
    print('【大模型输出】\n', action_plan_json)
    # 获取动作编排
    agent_plan_list = action_plan_json['action']
    # 获取AI回复
    ai_response = action_plan_json['response']
        
    return agent_plan_list, ai_response

# 函数：智能体Agent编排动作
# 扣子Coze智能体
import requests

def agent_plan_coze(question="先鞠个躬，再打个招呼，蹲下，最后站起来"):

    my_bot_id = '7433618606019100687'
    
    ## 以下无需修改
    # 构建HTTP请求
    url = 'https://api.coze.cn/v3/chat'
    headers = {
        'Authorization': COZE_AUTH,
        'Content-Type': 'application/json'
    }
    data = {
        "bot_id": my_bot_id,
        "user_id": "123",
        "stream": True,
        "auto_save_history": True,
        "additional_messages": [
            {
                "role": "user",
                "content": question,
                "content_type": "text"
            }
        ]
    }
    # 发起HTTP请求
    response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
    response_list = []
    if response.status_code == 200:
        response.encoding = "utf-8"
        # 假设响应是文本流
        for line in response.iter_lines(decode_unicode=True):
            response_list.append(line)
    else:
        print(f"Failed to get response from api, status code: {response.status_code}")
    
    # 解析AI回复信息
    for idx, each in enumerate(response_list):
        try:
            response_line = eval(each[5:])
            if response_line['type'] == 'verbose': # 工具调用响应
                answer = eval(response_list[idx-3][5:])['content']
                action_plan_json = eval(answer)
        except:
            pass

    print('【大模型输出】\n', action_plan_json)
    
    agent_plan_list = action_plan_json['action']
    ai_response = action_plan_json['response']
    
    return agent_plan_list, ai_response

# 函数：智能体Agent编排动作
# 亚马逊云科技 Amazon Bedrock
import boto3
from botocore.exceptions import ClientError
def agent_plan_bedrock(question="先鞠个躬，再打个招呼，蹲下，最后站起来"):

    # 选择大模型
    model_id = "anthropic.claude-3-5-haiku-20241022-v1:0"
    # model_id = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
    # model_id = 'meta.llama3-70b-instruct-v1:0'
    
    # # 获取可用模型列表及 Model ID
    # bedrock = boto3.client(service_name='bedrock',)
    # model_list = bedrock.list_foundation_models(byOutputModality='TEXT')['modelSummaries']
    # model_list

    # 构建 Amazon Bedrock client
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    
    PROMPT = robot_order_template + question
    
    # 构建请求体
    request_body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "temperature": 0.7,
        "messages": [
            {"role": "user", "content": PROMPT}
        ]
    })
    try:
        # 发起请求
        response = bedrock_runtime.invoke_model(modelId=model_id, body=request_body)
    
        # 解析响应内容
        response_body = json.loads(response['body'].read())
        # print("Response:", response_body['content'][0]['text'])
        action_plan_json = eval(response_body['content'][0]['text'])
        print('【大模型输出】\n', action_plan_json)
        
        agent_plan_list = action_plan_json['action']
        ai_response = action_plan_json['response']
        return agent_plan_list, ai_response
    except Exception as e:
        print(f"Unexpected error: {str(e)}")