# 常用函数
# 同济子豪兄 2024-11-5

import os
import json
from API_KEY import *

# 开发板IP地址
PI_IP = '192.168.31.141'

# 录音+语音识别
def asr_aipc():
    print('开始录音')
    terminal = 'ssh pi@{} "python TonyPi/OpenVINO/utils_asr.py"'.format(PI_IP)
    os.system(terminal)
    print('开始语音识别')
    terminal = 'scp pi@{}:~/TonyPi/OpenVINO/temp/speech_recognition.txt temp/speech_recognition.txt'.format(PI_IP)
    os.system(terminal)
    with open('temp/speech_recognition.txt', 'r', encoding='utf-8') as f:
        speech_result = f.read()
    print('【语音识别结果】', speech_result)
    return speech_result

# 语音合成+播放
def tts(ai_response):
    # 写入文件
    with open('temp/ai_response.txt', 'w', encoding='utf-8') as f:
        f.write(ai_response)
        
    # 传到开发板
    terminal = 'scp temp/ai_response.txt pi@{}:~/TonyPi/OpenVINO/temp/'.format(PI_IP)
    os.system(terminal)
    print('开始语音合成')
    terminal = 'ssh pi@{} "python ~/TonyPi/OpenVINO/utils_tts.py"'.format(PI_IP)
    os.system(terminal)
    # print('播放完成')

def play_welcome():
    print('播放欢迎音乐')
    terminal = 'ssh pi@{} "aplay -t wav /home/pi/TonyPi/OpenVINO/asset/welcome.wav -q"'.format(PI_IP)
    os.system(terminal)

def load_qwen_ov():
    import openvino_genai as ov_genai
    # 载入OpenVINO IR格式的大模型
    print('载入OpenVINO IR格式大模型')
    device = 'GPU'
    pipe = ov_genai.LLMPipeline("Qwen2-7B-Instruct-int4-ov", device)
    print('Qwen2-7B-Instruct模型载入完成')
    return pipe

# 提示词：智能体Agent编排动作
robot_order_template = '''
你是我的机器人，请你根据我的指令，以json形式输出接下来要运行的对应函数和你给我的回复
你只需要回答一个列表即可，不要回答任何中文
【以下是所有动作函数】
站立：stand()
原地踏步：stepping()
前进一步：move_forward()
后退一步：move_back()
向左平移移动一步：move_left()
向右平移移动一步：move_right()
向左旋转移动：turn_left()
向右旋转移动：turn_right()
鞠躬：bow()
挥手打招呼：wave()
扭腰：twist()
捶胸庆祝：celebrate()
下蹲：squat()
踢右脚：right_shot()
踢左脚：left_shot()
仰卧起坐：sit_ups()
佛山叶问的咏春拳：wing_chun()
从前倾趴卧起立，也就是从趴下到站起来：stand_up_front()
从后仰躺倒起立，也就是从躺下到站起来：stand_up_back()
巡线跨栏模式，顺着黑色线前进并跨越台阶等障碍物：athletics()
播放音乐并跳舞（唱跳RAP）：rap()
踢不同颜色的足球：kickball('red')
搬运不同颜色的海绵方块：transport('red green blue')

【输出限制】
你直接输出json即可，从{开始，以}结束，不要输出包含```json的开头或结尾
在'action'键中，输出函数名列表，列表中每个元素都是字符串，代表要运行的函数名称和参数。每个函数既可以单独运行，也可以和其他函数先后运行。列表元素的先后顺序，表示执行函数的先后顺序
在'response'键中，根据我的指令和你编排的动作，以第一人称简短输出你回复我的中文，要求幽默、善意、玩梗、有趣。不要超过20个字，不要回复英文。
如果我让你从躺倒状态站起来，你回复一些和“躺平”相关的话
kickball和transport函数需要用双引号

【以下是一些具体的例子】
我的指令：请你先鞠个躬，然后挥挥手。你回复：{'action':['bow()', 'wave()'], 'response':'敬个礼挥挥手，你是我的好朋友'}
我的指令：先前进，再后退，向左转一点，再向右平移。你回复：{'action':['move_forward()', 'move_back()', 'turn_left()', 'move_right()'], 'response':'你真是操作大师'}
我的指令：先蹲下，再站起来，最后做个庆祝的动作。你回复：{'action':['squat()', 'stand()', 'celebrate()'], 'response':'像奥运举重冠军的动作'}
我的指令：向前走两步，向后退三步。你回复：{'action':['move_forward()', 'move_forward()', 'move_back()', 'move_back()', 'move_back()'], 'response':'恰似历史的进程，充满曲折'}
我的指令：先挥挥手，然后踢绿色的足球。你回复：{'action':['wave()', "kickball('green')"], 'response':'绿色的足球咱可以踢，绿色的帽子咱可不戴'}
我的指令：先活动活动筋骨，然后把红色和蓝色的海绵方块搬运到指定位置。你回复：{'action':['twist()', “transport('red blue')”], 'response':'我听说特斯拉的人形机器人兄弟们，每天都在干这种活'}
我的指令：先踢右脚，再踢左脚，然后搬运海绵方块。你回复：{'action':['right_shot()', 'left_shot()', “transport('red green blue')”], 'response':'让我先活动活动，然后让海绵宝宝们各回各家'}
我的指令：别躺着了，快起来，把红色和蓝色方块搬运到指定位置。你回复：{'action':['stand_up_back()', “transport('red blue')”], 'response':'我也想躺平啊，奈何得干活儿'}

【我现在的指令是】
'''

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
# 零一万物
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
    
# 函数：将编排好的动作传输给树莓派并运行
def send_txt(agent_plan_list):
    agent_plan_str = str(agent_plan_list)
    # 写入txt文件
    with open('temp/agent_plan.txt', 'w') as f:
        f.write(agent_plan_str)
    # 把动作编排txt文件传到开发板
    terminal = 'scp temp/agent_plan.txt pi@{}:~/TonyPi/OpenVINO/temp/'.format(PI_IP)
    os.system(terminal)
    



    

