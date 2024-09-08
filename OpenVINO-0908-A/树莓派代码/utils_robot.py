# 机器人动作函数
# 同济子豪兄 2024-9-7

# 导入工具包
import sys
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

# 田径运动：巡线、跨栏、上下台阶
def athletics():
    os.system('python ../Extend/athletics_course/athletics_perform_only.py')

# 唱跳RAP
def rap():
    os.system('python Extend/sensor_development/little_apple.py')

# bow()
# print('鞠躬')

# if __name__ == '__main__':

print('开始依次执行动作')

with open('/home/pi/TonyPi/OpenVINO/temp/agent_plan.txt', 'r', encoding='utf-8') as f:
    agent_plan = f.read()
try:
    agent_plan = eval(agent_plan)
except:
    print('动作为空，退出')
    exit()

print('载入动作列表', agent_plan)

# 依次执行每个动作
for action in agent_plan:
    print('开始动作', action)
    eval(action)