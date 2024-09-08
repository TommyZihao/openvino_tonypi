# 启动语音控制机器人
# 同济子豪兄 2024-9-8

import os
import openvino_genai as ov_genai
from utils_zihao import *

# 载入OpenVINO IR格式的大模型
print('载入OpenVINO IR格式大模型')
device = 'GPU'
pipe = ov_genai.LLMPipeline("Qwen2-7B-Instruct-int4-ov", device)
print('模型载入完成')
play_welcome()


def agent_play():

    start = input('输入1开始录音')
    
    if start == '1':
        
        # 录音+语音识别
        speech_result = asr_aipc()
        
        # 智能体编排动作
        agent_plan_list, ai_response = agent_plan_qwen_ov(pipe, speech_result)
    
        # 语音合成
        tts(ai_response)
    
        # 依次执行动作
        terminal = 'ssh pi@{} "python ~/TonyPi/OpenVINO/utils_robot.py"'.format(PI_IP)
        os.system(terminal)
        print('所有动作完成')
    

    

    

