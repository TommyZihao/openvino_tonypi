# 播放歌曲“小苹果”并跳舞
# 同济子豪兄 2024-8-29

import time
import hiwonder.ros_robot_controller_sdk as rrc
from hiwonder.Controller import Controller
import hiwonder.MP3 as MP3
import hiwonder.ActionGroupControl as AGC
import hiwonder.yaml_handle as yaml_handle

board = rrc.Board()

move_st = True
servo_data = yaml_handle.get_yaml_data(yaml_handle.servo_file_path)
servo2_pulse = servo_data['servo2']

# 初始位置
ctl = Controller(board)
ctl.set_pwm_servo_pulse(1, 1500, 500)
ctl.set_pwm_servo_pulse(2, servo_data['servo2'], 500)

num = 0
time_ = 0
touch = False
state = True
pause_en = False
time_wait = False
    
addr = 0x7b         #传感器iic地址(sensor I2C address)
mp3 = MP3.MP3(addr)
AGC.runActionGroup('stand_slow')
AGC.runActionGroup('bow')
board.set_buzzer(1900, 0.1, 0.9, 1)

# 选择播放的歌曲
num_ = 1

if num_ == 1:
    pause_en = True
    mp3.volume(30)  # 设置音量
    mp3.playNum(18) # 播放歌曲18：小苹果
    time.sleep(0.8)
    AGC.runActionGroup('18')
elif num_ == 2:
    pause_en = True
    mp3.volume(30) 
    mp3.playNum(22) 
    time.sleep(0.8)
    AGC.runActionGroup('22')
elif num_ == 3:
    pause_en = True
    mp3.volume(30) 
    mp3.playNum(24) 
    time.sleep(0.8)
    AGC.runActionGroup('24')
else:
    time.sleep(0.3)
    board.set_buzzer(1900, 0.2, 0.8, 1) 
    time.sleep(0.1)
    board.set_buzzer(1900, 0.2, 0.8, 1)

AGC.runActionGroup('bow')



    
    
