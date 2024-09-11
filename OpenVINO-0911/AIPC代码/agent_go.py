# 启动语音控制机器人
# 同济子豪兄 2024-9-8

import os
import time
from utils_zihao import *

# 播放欢迎音乐
play_welcome()

# 选择大模型
MODEL = 'qwen'     # Qwen2-7B-Instruct本地部署
# MODEL = 'yi'     # 零一万物 API
# MODEL = 'ernie'  # 百度文心大模型 API

if MODEL == 'qwen':
    pipe = load_qwen_ov()

def agent_play():

    start = input('输入1进入语音动作模式，输入2进入语音视觉模式，输入3进入文字动作模式，输入4进入文字视觉模式：')

    print('start', start)

    if (start == '3') or (start == '4'):
        speech_result = input('请输入文字指令：')
    else:
        speech_result = asr_aipc() # 录音+语音识别

    print('开始调用大模型')
    START_TIME = time.time() # 开始计时
    
    # 智能体编排动作
    if MODEL == 'qwen':
        agent_plan_list, ai_response = agent_plan_qwen_ov(pipe, speech_result)
    elif MODEL == 'yi':
        agent_plan_list, ai_response = agent_plan_yi(speech_result)
    elif MODEL == 'ernie':
        agent_plan_list, ai_response = agent_plan_qianfan(speech_result) # 百度千帆大模型平台

    WAIT_TIME = time.time() - START_TIME
    print('大模型耗时 {:.2f} 秒'.format(WAIT_TIME))

    # 语音合成
    tts(ai_response)
    
    if (start=='1') or (start=='3'):
        # 依次执行动作
        terminal = 'ssh pi@{} "export DISPLAY=:0 && python ~/TonyPi/OpenVINO/utils_robot.py"'.format(PI_IP)
        os.system(terminal)
        print('所有动作完成')
        
    elif (start=='2') or (start=='4'):
        print('请在开发板桌面运行 python ~/TonyPi/OpenVINO/utils_robot.py')

    

    

