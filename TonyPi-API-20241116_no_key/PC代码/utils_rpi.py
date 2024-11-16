# 机器人树莓派常用函数
# 同济子豪兄 2024-11-5

import os
import json

# 开发板IP地址
PI_IP = '192.168.31.146'

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
    
# 函数：将编排好的动作传输给树莓派并运行
def send_txt(agent_plan_list):
    agent_plan_str = str(agent_plan_list)
    # 写入txt文件
    with open('temp/agent_plan.txt', 'w') as f:
        f.write(agent_plan_str)
    # 把动作编排txt文件传到开发板
    terminal = 'scp temp/agent_plan.txt pi@{}:~/TonyPi/OpenVINO/temp/'.format(PI_IP)
    os.system(terminal)
    



    

