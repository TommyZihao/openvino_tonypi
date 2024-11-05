# 机器人动作函数
# 同济子豪兄 2024-9-7

# 导入工具包
import os
import hiwonder.ActionGroupControl as AGC

# 站立
def stand():
    AGC.runActionGroup('stand')

# 前进
def move_forward():
    AGC.runActionGroup('go_forward')

# 后退
def move_back():
    AGC.runActionGroup('back_fast')

# 向左移动
def move_left():
    AGC.runActionGroup('left_move_fast')

# 向右移动
def move_right():
    AGC.runActionGroup('right_move_fast')

# 向左旋转
def turn_left():
    AGC.runActionGroup('turn_left')

# 向右旋转
def turn_right():
    AGC.runActionGroup('turn_right')

# 鞠躬
def bow():
    AGC.runActionGroup('bow')

# 挥手
def wave():
    AGC.runActionGroup('wave')
    
# 扭腰
def twist():
    AGC.runActionGroup('twist')

# 庆祝
def celebrate():
    AGC.runActionGroup('chest')

# 下蹲
def squat():
    AGC.runActionGroup('squat')

# 踢右脚
def right_shot():
    AGC.runActionGroup('right_shot_fast')

# 踢左脚
def left_shot():
    AGC.runActionGroup('left_shot_fast')

# 仰卧起坐
def sit_ups():
    AGC.runActionGroup('sit_ups')

# 原地踏步
def stepping():
    AGC.runActionGroup('stepping')

# 打佛山叶问的咏春拳
def wing_chun():
    AGC.runActionGroup('wing_chun')

# 前倾跌倒起立
def stand_up_front():
    AGC.runActionGroup('stand_up_front')

# 后仰跌倒起立
def stand_up_back():
    AGC.runActionGroup('stand_up_back')
    
# 田径运动：巡线、跨栏、上下台阶
def athletics():
    os.system('python /home/pi/TonyPi/Extend/athletics_course/athletics_perform_only.py')

# 唱跳RAP
def rap():
    os.system('python /home/pi/TonyPi/Extend/sensor_course/sensor_development/little_apple.py')

# 踢足球
def kickball(color='red'):
    terminal = 'python /home/pi/TonyPi/Functions/KickBall_only_once.py {}'.format(color)
    print('terminal', terminal)
    os.system(terminal)

# 搬运海绵方块
def transport(color_list_str='red green blue'):
    color_list = color_list_str.split(' ')
    terminal = 'python /home/pi/TonyPi/Functions/Transport_only.py "{}"'.format(color_list)
    print('terminal', terminal)
    os.system(terminal)
    
# bow()
# print('鞠躬')

# if __name__ == '__main__':

print('Actions Step-by-Step')

with open('/home/pi/TonyPi/OpenVINO/temp/agent_plan.txt', 'r', encoding='utf-8') as f:
    agent_plan = f.read()
try:
    agent_plan = eval(agent_plan)
except:
    print('动作为空，退出')
    exit()

print('Agent Action List:', agent_plan)

# 依次执行每个动作
for action in agent_plan:
    print('Action:', action)
    eval(action)