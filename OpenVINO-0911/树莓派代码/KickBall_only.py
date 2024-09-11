#!/usr/bin/python3
# coding=utf8
import sys
import os
import cv2
import time
import math
import threading
import numpy as np

import hiwonder.PID as PID
import hiwonder.Misc as Misc
import hiwonder.Camera as Camera
import hiwonder.ros_robot_controller_sdk as rrc
from hiwonder.Controller import Controller
import hiwonder.ActionGroupControl as AGC
import hiwonder.yaml_handle as yaml_handle



'''
    程序功能：自动踢球(program function: auto shooting)

    运行效果：将红色小球放置在机器人摄像头前，在识别到后机器人将会调整位置靠向小球，并将其
             踢向前方。(running effect: place the red ball in front of the robot's camera. Once recognized, the robot will adjust its position towards the ball and kick it forward)

    对应教程文档路径：  TonyPi智能视觉人形机器人\3.AI视觉玩法学习\第2课 自动踢球(corresponding tutorial file path: TonyPi Intelligent Vision Humanoid Robot\3.AI Vision Game Course\Lesson2 Auto Shooting)
'''

if __name__ == '__main__':
    from CameraCalibration.CalibrationConfig import *
else:
    from Functions.CameraCalibration.CalibrationConfig import *


# 调试模式标志量(debug mode flag variable)
debug = False

# 检查 Python 版本是否为 Python 3，若不是则打印提示信息并退出程序(check if the Python version is Python 3. If not, print a prompt message and exit the program)
if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

#加载参数(load parameters)
param_data = np.load(calibration_param_path + '.npz')

#获取参数(get parameters)
mtx = param_data['mtx_array']
dist = param_data['dist_array']
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (640, 480), 0, (640, 480))
mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (640, 480), 5)

range_rgb = {
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}

# 找出面积最大的轮廓(find out the contour with the maximal area)
# 参数为要比较的轮廓的列表(parameter is the list of contour to be compared)
def getAreaMaxContour(contours):
    contour_area_temp = 0
    contour_area_max = 0
    areaMaxContour = None

    for c in contours:  # 历遍所有轮廓(iterate through all contours)
        contour_area_temp = math.fabs(cv2.contourArea(c))  # 计算轮廓面积(calculate contour area)
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if 1000 > contour_area_temp > 2:  # 只有在面积大于300时，最大面积的轮廓才是有效的，以过滤干扰(only contours with an area greater than 300 are considered valid; the contour with the largest area is used to filter out interference)
                areaMaxContour = c

    return areaMaxContour, contour_area_max  # 返回最大的轮廓(return the contour with the maximal area)

board = rrc.Board()
ctl = Controller(board)

# 设置需要检测的球的颜色，默认为红色(set the color of the ball to be detected, defaulting to red)
__target_color = ('red')

# 设置球的目标颜色(set the target color of the ball)
def setBallTargetColor(target_color):
    global __target_color

    __target_color = target_color
    return (True, (), 'SetBallColor')

# 颜色阈值数据和头部舵机位置数据(color threshold data and head servo position data)
lab_data = None
servo_data = None

# 加载配置文件数据(load configuration file data)
def load_config():
    global lab_data, servo_data
    
    lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
    servo_data = yaml_handle.get_yaml_data(yaml_handle.servo_file_path)                                

load_config()

# 初始化机器人舵机初始位置(initialize the servo initialization position of robot)
def initMove():
    ctl.set_pwm_servo_pulse(1, servo_data['servo1'], 500)
    ctl.set_pwm_servo_pulse(2, servo_data['servo2'], 500)


# 初始化开始计时的时间戳(initialize the timestamp for starting the timer)
t1 = 0

# 初始化舵机移动水平方向和垂直方向的步长(initialize the step size for servo movement in the horizontal and vertical directions)
d_x = 20
d_y = 20

# 初始化主步骤step（检测到球时的情况）和子步骤step_（未检测到球时的情况）(initialize the main step (when the ball is detected) and sub-step (when the ball is not detected))
step = 1
step_ = 1

# 设置舵机位置(set servo position)
x_dis = servo_data['servo2']
y_dis   = servo_data['servo1']

# 初始化机器人上一步的状态(initialize the previous state of the robot)
last_status = ''

# 初始化开始计时的标志量(initialize the flag variable for starting the timer)
start_count= True

# 初始化球的中心坐标(initialize the center coordinates of ball)
CenterX, CenterY = -2, -2

# 初始化 PID 控制器(initialize PID controller)
x_pid = PID.PID(P=0.145, I=0.00, D=0.0007)
y_pid = PID.PID(P=0.145, I=0.00, D=0.0007)


# 重置所有变量为初始状态(reset all the variable to initial state)
def reset():
    global t1                         
    global d_x, d_y
    global last_status
    global start_count
    global step, step_
    global x_dis, y_dis
    global __target_color
    global CenterX, CenterY

    t1 = 0
    d_x = 20
    d_y = 20
    step = 1
    step_ = 1
    x_pid.clear()
    y_pid.clear()
    x_dis = servo_data['servo2']
    y_dis = servo_data['servo1']
    last_status = ''
    start_count= True
    __target_color = ()
    CenterX, CenterY = -2, -2

    
# app初始化调用(app initialization calling)
def init():
    print("kick_ball Init")
    load_config()
    initMove()

# 机器人是否运行的标志量(the flag variable indicating whether the robot is running)
__isRunning = False

# app开始玩法调用(app start program calling)
def start():
    global __isRunning
    reset()
    __isRunning = True
    print("KickBall Start")

# app停止玩法调用(app stop program calling)
def stop():
    global __isRunning
    __isRunning = False
    print("KickBall Stop")

# app退出玩法调用(app exit program calling)
def exit():
    global __isRunning
    __isRunning = False
    AGC.runActionGroup('stand_slow')
    print("KickBall Exit")


# 图像中心横坐标(the horizontal coordinate of the image center)
CENTER_X = 320

#机器人运动控制(robot movement control)
def move():
    global t1                   
    global d_x         
    global d_y           
    global step                    
    global step_                     
    global x_dis    
    global y_dis     
    global last_status            
    global start_count           
    global __isRunning             
    
    while True:
        if debug:      # 如果 debug 模式打开，则直接返回不执行后面的操作(if the debug mode is enabled, return directly without executing the subsequent operations)
            return
        if __isRunning:
           
            if CenterX >= 0:      # 如果检测到了球(if the ball is detected)
                step_ = 1                      
                d_x, d_y = 20, 20
                start_count= True            # 开始计时标志置为True，在后面找不到球的情况下使用(the flag for starting the timer is set to True, to be used when the ball is not found later on)
               
                if step == 1:      
                    # 球不在画面中心，则根据方向让机器人转向一步，直到满足条件进入步骤2(if the ball is not in the center of the frame, instruct the robot to turn one step in the direction until the condition is met to enter step 2)
                    if x_dis - servo_data['servo2'] > 150:
                        AGC.runActionGroup('turn_left_small_step')
                    elif x_dis - servo_data['servo2'] < -150:
                        AGC.runActionGroup('turn_right_small_step')
                    else:
                        step = 2

                elif step == 2:
                    # 当控制头部垂直运动的舵机位置等于设定的位置(when the position of the servo controlling vertical head movement equals the set position)
                    if y_dis == servo_data['servo1']:     
                        # 根据当前水平舵机位置调整机器人运动(adjust the robot's movement based on the current horizontal servo position)
                        if x_dis == servo_data['servo2'] - 400:
                            AGC.runActionGroup('turn_right',2)
                        elif x_dis == servo_data['servo2'] + 400:
                            AGC.runActionGroup('turn_left',2)
                        elif 350 < CenterY <= 380:    # ball_center_y值越大，与球的距离越近(the larger the value of ball_center_y, the closer the distance to the ball)
                            AGC.runActionGroup('go_forward_one_step')
                            last_status = 'go'        # 记录上一步的状态是往前走(record the previous step state as walking forward)
                            step = 1
                        elif 120 < CenterY <= 350:
                            AGC.runActionGroup('go_forward')
                            last_status = 'go'
                            step = 1
                        elif 0 <= CenterY <= 120 and abs(x_dis - servo_data['servo2']) <= 200:
                            AGC.runActionGroup('go_forward_fast')
                            last_status = 'go'
                            step = 1
                        else:
                            step = 3
                    else:
                        # 当控制头部垂直运动的舵机位置不等于设定的位置，机器人调整位置往前走，直到两个位置相等(when the position of the servo controlling vertical head movement is not equal to the set position, the robot adjusts its position to move forward until the two positions are equal)
                        if x_dis == servo_data['servo2'] - 400:
                            AGC.runActionGroup('turn_right',2)
                        elif x_dis == servo_data['servo2'] + 400:
                            AGC.runActionGroup('turn_left',2)
                        else:
                            AGC.runActionGroup('go_forward_fast')
                            last_status = 'go'

                elif step == 3:
                    if y_dis == servo_data['servo1']:
                        # 根据球在画面的x坐标左右平移调整位置(adjust the position based on the left-right movement of the ball's x-coordinate in the frame)
                        if abs(CenterX - CENTER_X) <= 40:
                            AGC.runActionGroup('left_move')
                        elif 0 < CenterX < CENTER_X - 50 - 40:
                            AGC.runActionGroup('left_move_fast')
                            time.sleep(0.2)
                        elif CENTER_X + 50 + 40 < CenterX:                      
                            AGC.runActionGroup('right_move_fast')
                            time.sleep(0.2)
                        else:
                            step = 4 
                    else:
                        if 270 <= x_dis - servo_data['servo2'] < 480:
                            AGC.runActionGroup('left_move_fast')
                            time.sleep(0.2)
                        elif abs(x_dis - servo_data['servo2']) < 170:
                            AGC.runActionGroup('left_move')
                        elif -480 < x_dis - servo_data['servo2'] <= -270:                      
                            AGC.runActionGroup('right_move_fast')
                            time.sleep(0.2)
                        else:
                            step = 4                   
                elif step == 4:
                    if y_dis == servo_data['servo1']:
                        # 小步伐靠近到合适的距离(take small steps to approach at the appropriate distance)
                        if 380 < CenterY <= 440:
                            AGC.runActionGroup('go_forward_one_step')
                            last_status = 'go'
                        elif 0 <= CenterY <= 380:
                            AGC.runActionGroup('go_forward')
                            last_status = 'go'
                        else:   # 根据最后球的x坐标，采用离得近的脚去踢球(use closest foot to kick the ball based on the final x-coordinates of the ball)
                            AGC.runActionGroup('go_forward_one_step')
                            if CenterX < CENTER_X:
                                AGC.runActionGroup('left_shot_fast')
                            else:
                                AGC.runActionGroup('right_shot_fast')
                            step = 1
                    else:
                        step = 1

            elif CenterX == -1:   # 如果没检测到球(if no ball is detected)
                # 如果机器人上次状态为“前进”，快速后退一步(if the robot's previous state was 'forward,' quickly take one step backward)
                if last_status == 'go':
                    last_status = ''
                    AGC.runActionGroup('back_fast', with_stand=True)                   
                elif start_count:  # 开始计时的标志变量为True(the flag variable for starting the timer is set to True)
                    start_count= False
                    t1 = time.time()    # 记录当前的时间，开始计时(record the current time and start the timer)
                else:
                    if time.time() - t1 > 0.5:
                        
                        if step_ == 5:
                            x_dis += d_x
                            if abs(x_dis - servo_data['servo2']) <= abs(d_x):
                                AGC.runActionGroup('turn_right')
                                step_ = 1
                        if step_ == 1 or step_ == 3:
                            x_dis += d_x            
                            if x_dis > servo_data['servo2'] + 400:
                                if step_ == 1:
                                    step_ = 2
                                d_x = -d_x
                            elif x_dis < servo_data['servo2'] - 400:
                                if step_ == 3:
                                    step_ = 4
                                d_x = -d_x
                        elif step_ == 2 or step_ == 4:
                            y_dis += d_y
                            if y_dis > 1200:
                                if step_ == 2:
                                    step_ = 3
                                d_y = -d_y
                            elif y_dis < servo_data['servo1']:
                                if step_ == 4:                                
                                    step_ = 5
                                d_y = -d_y
                        ctl.set_pwm_servo_pulse(1, y_dis, 20)
                        ctl.set_pwm_servo_pulse(2, x_dis, 20)
                        
                        time.sleep(0.02)
            else:
                time.sleep(0.01)
        else:
            time.sleep(0.01)

#启动动作的线程(start the thread of executing action)
th = threading.Thread(target=move)
th.daemon = True
th.start()

size = (320, 240)

def run(img):
    global x_dis, y_dis
    global CenterX, CenterY
    global last_status

    img_copy = img.copy()
    img_h, img_w = img.shape[:2]    # 获取图像高度和宽度(get the height and width of the image)

    if not __isRunning or __target_color == ():
        # 如果robot_is_running不为True或者没有设置球的颜色(if robot_is_running is not True or the ball color is not set)
        if debug:
            # 在调试模式下输出参考线(in debug mode, output reference lines)
            cv2.line(img, (0, 450), (img_w, 450), (0, 255, 255), 2)
            cv2.line(img, (0, 380), (img_w, 380), (0, 255, 255), 2)
            cv2.line(img, (0, 300), (img_w, 300), (0, 255, 255), 2)
        return img
    
    # 重新调整图像大小(resize the image)
    frame_resize = cv2.resize(img_copy, size, interpolation=cv2.INTER_NEAREST)
    # 高斯模糊(Gaussian blur)
    frame_gb = cv2.GaussianBlur(frame_resize, (3, 3), 3)
    # 将图像转换到LAB色彩空间(convert the image to LAB color space)
    frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  
    
    area_max = 0
    areaMaxContour = 0
    for i in lab_data:
        if i in __target_color:
            detect_color = i
            #对原图像和掩模进行位运算(perform bitwise operation to the original image and mask)
            frame_mask = cv2.inRange(frame_lab,
                                         (lab_data[i]['min'][0],
                                          lab_data[i]['min'][1],
                                          lab_data[i]['min'][2]),
                                         (lab_data[i]['max'][0],
                                          lab_data[i]['max'][1],
                                          lab_data[i]['max'][2]))  
            #腐蚀(corrosion)
            eroded = cv2.erode(frame_mask, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))  
            #膨胀(dilation)
            dilated = cv2.dilate(eroded, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))) 
            if debug:
                # 在调试模式下显示掩模(display mask in the debug mode)
                cv2.imshow(i, dilated)
            contours = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # 找出轮廓(find out contour)
            # 找出设定范围内的最大轮廓，返回轮廓和轮廓的面积(find the largest contour within the specified range and return the contour and its area)
            areaMaxContour, area_max = getAreaMaxContour(contours)  
    if area_max:  # 如果找到最大面积的轮廓(if the contour with the maximal area is found)
        try:
            (CenterX, CenterY), radius = cv2.minEnclosingCircle(areaMaxContour) #获取最小外接圆(get the minimum circumcircle)
        except:
            img = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)  # 畸变矫正(distortion correction)
            return img
        # 将球的中心坐标和半径映射回原始图像尺寸(map the center coordinates and radius of the ball back to the original image size)
        CenterX = int(Misc.map(CenterX, 0, size[0], 0, img_w))
        CenterY = int(Misc.map(CenterY, 0, size[1], 0, img_h))
        radius = int(Misc.map(radius, 0, size[0], 0, img_w))
        use_time = 0       
        
        if y_dis == servo_data['servo1'] and abs(x_dis - servo_data['servo2']) < 150:
            x_dis = servo_data['servo2']
        else:
            # 设置水平舵机位置PID的目标值为图像宽度的一半(set the target value of the PID for the horizontal servo position to half of the image width)
            x_pid.SetPoint = img_w / 2
            
            x_pid.update(CenterX)

            d_x = int(x_pid.output)
           
            last_status = 'left' if d_x > 0 else 'right'
            # 计算使用时间(calculate usage time)
            use_time = abs(d_x * 0.00025)
            x_dis += d_x    

            # 将控制头部水平移动的舵机位置限制在预设范围内(limit the position of the servo controlling horizontal head movement within the preset range)
            x_dis = servo_data['servo2'] - 400 if x_dis < servo_data['servo2'] - 400 else x_dis          
            x_dis = servo_data['servo2'] + 400 if x_dis > servo_data['servo2'] + 400 else x_dis
            
        # 设置垂直舵机位置PID的目标值为图像高度的一半(set the target value of the PID for the vertical servo position to half of the image height)
        y_pid.SetPoint = img_h / 2
        y_pid.update(CenterY)
        
        d_y = int(y_pid.output)
        # 计算使用时间(calculate usage time)
        use_time = round(max(use_time, abs(d_y * 0.00025)), 5)
        # 更新垂直舵机位置(update vertical servo position)
        y_dis += d_y
        
        # 将控制头部垂直移动的舵机位置限制在预设范围内(limit the position of the servo controlling vertical head movement within the preset range)
        y_dis = servo_data['servo1'] if y_dis < servo_data['servo1'] else y_dis
        y_dis = 1200 if y_dis > 1200 else y_dis    
        
        ctl.set_pwm_servo_pulse(1, y_dis, use_time*1000)
        ctl.set_pwm_servo_pulse(2, x_dis, use_time*1000)
        time.sleep(use_time)
        
        # 在图像上绘制球的轮廓和参考线(draw the contour of the ball and reference lines on the image)
        cv2.circle(img, (CenterX, CenterY), radius, range_rgb[detect_color], 2)
        cv2.line(img, (int(CenterX - radius/2), CenterY), (int(CenterX + radius/2), CenterY), range_rgb[detect_color], 2)
        cv2.line(img, (CenterX, int(CenterY - radius/2)), (CenterX, int(CenterY + radius/2)), range_rgb[detect_color], 2)
    else:
        # 未识别到球时x，y坐标均返回-1(when the ball is not recognized, both the x and y coordinates return -1)
        CenterX, CenterY = -1, -1
   
    if debug:
        # 在调试模式下显示舵机位置和参考线(in debug mode, display the servo position and reference lines)
        cv2.putText(img, "x_dis: " + str(x_dis), (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, range_rgb[detect_color], 2)
        cv2.line(img, (0, 450), (img_w, 450), (0, 255, 255), 2)
        cv2.line(img, (0, 380), (img_w, 380), (0, 255, 255), 2)
        cv2.line(img, (0, 300), (img_w, 300), (0, 255, 255), 2) 

    return img

if __name__ == '__main__':
    debug = False
    if debug:
        print('Debug Mode')
    
    init()
    start()

    color = sys.argv[1]
    if color == []:
        color = 'red'

    __target_color = (color)
    
    open_once = yaml_handle.get_yaml_data('/boot/camera_setting.yaml')['open_once']
    if open_once:
        my_camera = cv2.VideoCapture('http://127.0.0.1:8080/?action=stream?dummy=param.mjpg')
    else:
        my_camera = Camera.Camera()
        my_camera.camera_open()              
    AGC.runActionGroup('stand')
    while True:
        ret, img = my_camera.read()
        if ret:
            frame = img.copy()
            Frame = run(frame)           
            cv2.imshow('Frame', Frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    my_camera.camera_close()
    cv2.destroyAllWindows()
