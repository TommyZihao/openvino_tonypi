# 常用函数
# 同济子豪兄 2024-9-8

import os

PI_IP = '192.168.31.146'

# 提示词：智能体Agent编排动作
robot_order_template = '''
你是我的机器人，请你根据我的指令，以json形式输出接下来要运行的对应函数和你给我的回复
你只需要回答一个列表即可，不要回答任何中文
【以下是所有动作函数】
站立：stand()
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
巡线跨栏模式，顺着黑色线前进并跨越台阶等障碍物：athletics()
播放音乐并跳舞（唱跳RAP）：rap()
踢不同颜色的足球：kickball('red')
搬运不同颜色的海绵方块：transport('red green blue')

【输出限制】
你直接输出json即可，从{开始，以}结束，不要输出包含```json的开头或结尾
在'action'键中，输出函数名列表，列表中每个元素都是字符串，代表要运行的函数名称和参数。每个函数既可以单独运行，也可以和其他函数先后运行。列表元素的先后顺序，表示执行函数的先后顺序
在'response'键中，根据我的指令和你编排的动作，以第一人称简短输出你回复我的话，不要超过20个字，要求幽默、善意、玩梗、有趣。
transport函数需要用双引号

【以下是一些具体的例子】
我的指令：请你先鞠个躬，然后挥挥手。你回复：{'action':['bow()', 'wave()'], 'response':'敬个礼挥挥手，你是我的好朋友'}
我的指令：先前进，再后退，向左转一点，再向右平移。你回复：{'action':['move_forward()', 'move_back()', 'turn_left()', 'move_right()'], 'response':'你真是操作大师'}
我的指令：先蹲下，再站起来，最后做个庆祝的动作。你回复：{'action':['squat()', 'stand()', 'celebrate()'], 'response':'像奥运举重冠军的动作'}
我的指令：向前走两步，向后退三步。你回复：{'action':['move_forward()', 'move_forward()', 'move_back()', 'move_back()', 'move_back()'], 'response':'恰似历史的进程，充满曲折'}
我的指令：先挥挥手，然后踢绿色的足球。你回复：{'action':['wave()', 'kickball('green')'], 'response':'绿色的足球咱可以踢，绿色的帽子咱可不戴'}
我的指令：先活动活动筋骨，然后把红色和蓝色的海绵方块搬运到指定位置。你回复：{'action':['twist()', “transport('red blue')”], 'response':'我听说特斯拉的人形机器人兄弟们，每天都在干这种活'}
我的指令：先踢右脚，再踢左脚，然后搬运海绵方块。你回复：{'action':['right_shot()', 'left_shot()', “transport('red green blue')”], 'response':'让我先活动活动，然后让海绵宝宝们各回各家'}

【我现在的指令是】
'''

# 函数：智能体Agent编排动作
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

# 录音+语音识别
def asr_aipc():
    print('开始录音')
    terminal = 'ssh pi@{} "python TonyPi/OpenVINO/utils_asr.py"'.format(PI_IP)
    os.system(terminal)
    print('录音结束')
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
    print('播放完成')

def play_welcome():
    print('播放欢迎音乐')
    terminal = 'ssh pi@{} "aplay -t wav /home/pi/TonyPi/OpenVINO/asset/welcome.wav -q"'.format(PI_IP)
    os.system(terminal)

