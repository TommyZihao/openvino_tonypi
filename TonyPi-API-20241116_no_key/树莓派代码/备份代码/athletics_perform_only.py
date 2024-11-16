# /home/pi/TonyPi/Extend/athletics_course/athletics_perform_only.py

#!/usr/bin/python3
# coding=utf8
# 4.拓展课程学习\11.拓展课程之田径运动课程\第4课 田径运动(4.Advanced Lessons\11.Athletics Sport Lesson\Lesson4 Athletics Performance)
# 巡线+跨栏+避障+上下台阶
import os
import sys
import cv2
import time
import math
import threading
import numpy as np
import hiwonder.ros_robot_controller_sdk as rrc
from hiwonder.Controller import Controller
import hiwonder.Misc as Misc
import hiwonder.PID as PID
import hiwonder.ActionGroupControl as AGC
import hiwonder.yaml_handle as yaml_handle

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

# 田径表演(athletics performance)

go_forward = 'go_forward'
go_forward_one_step = 'go_forward_one_step'
turn_right = 'turn_right_small_step_a'
turn_left  = 'turn_left_small_step_a'        
left_move = 'left_move_20'
right_move = 'right_move_20'
go_turn_right = 'turn_right'
go_turn_left = 'turn_left'

lab_data = None
servo_data = None

def load_config():
    global lab_data, servo_data
    
    lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
    servo_data = yaml_handle.get_yaml_data(yaml_handle.servo_file_path)

load_config()

board = rrc.Board()
ctl = Controller(board)

# 初始位置(initial position)
def initMove():
    ctl.set_pwm_servo_pulse(1,servo_data['servo1'],500)
    ctl.set_pwm_servo_pulse(2,servo_data['servo2'],500)   

object_left_x, object_right_x, object_center_y, object_angle = -2, -2, -2, 0
switch = False
# 变量重置(variable reset)
def reset():
    global object_left_x, object_right_x
    global object_center_y, object_angle, switch
    
    switch = False
    object_left_x, object_right_x, object_center_y, object_angle = -2, -2, -2, 0
    
def init():
    load_config()
    initMove()
    reset()


# 找出面积最大的轮廓(find out the contour with the maximal area)
# 参数为要比较的轮廓的列表(the parameter is a list of contours to compare)
def getAreaMaxContour(contours, area_min=10):
    contour_area_temp = 0
    contour_area_max = 0
    area_max_contour = None

    for c in contours:  # 历遍所有轮廓(iterate through all contours)
        contour_area_temp = math.fabs(cv2.contourArea(c))  # 计算轮廓面积(calculate contour area)
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp >= area_min:  # 只有在面积大于设定值时，最大面积的轮廓才是有效的，以过滤干扰(only when the area is greater than the set value, the contour with the largest area is considered valid, to filter out interference)
                area_max_contour = c

    return area_max_contour, contour_area_max  # 返回最大的轮廓(return the contour with the maximal area)


line_centerx = 320
size = (640, 480)
roi = [ 
        (300, 340,  0, 640, 0.1), 
        (360, 400,  0, 640, 0.3), 
        (420, 480,  0, 640, 0.6)
      ]

roi_h1 = roi[0][0]
roi_h2 = roi[1][0] - roi[0][0]
roi_h3 = roi[2][0] - roi[1][0]
roi_h_list = [roi_h1, roi_h2, roi_h3]

#巡线视觉处理函数(line following vision processing function)
def line_patrol(img, img_draw, target_color = 'black'):
    
    n = 0
    center_ = []
    weight_sum = 0
    centroid_x_sum = 0
    
    img_h, img_w = img.shape[:2]
    frame_resize = cv2.resize(img_draw, size, interpolation=cv2.INTER_NEAREST)
    frame_gb = cv2.GaussianBlur(frame_resize, (3, 3), 3)   
    
    #将图像分割成上中下三个部分，这样处理速度会更快，更精确(divide the image into three parts: top, middle, and bottom. This approach will result in faster and more accurate processing)
    for r in roi:
        roi_h = roi_h_list[n]
        n += 1       
        blobs = frame_gb[r[0]:r[1], r[2]:r[3]]
        frame_lab = cv2.cvtColor(blobs, cv2.COLOR_BGR2LAB)  # 将图像转换到LAB空间(convert the image to LAB space)
        
        frame_mask = cv2.inRange(frame_lab,
                                     (lab_data[target_color]['min'][0],
                                      lab_data[target_color]['min'][1],
                                      lab_data[target_color]['min'][2]),
                                     (lab_data[target_color]['max'][0],
                                      lab_data[target_color]['max'][1],
                                      lab_data[target_color]['max'][2]))  #对原图像和掩模进行位运算(operate bitwise operation to original image and mask)
        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # 开运算(opening operation)
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # 闭运算(closing operation)
        cnts = cv2.findContours(closed , cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)[-2]#找出所有轮廓(find out all contours)
        cnt_large, area = getAreaMaxContour(cnts)#找到最大面积的轮廓(find out the contour with the maximal area)
        if cnt_large is not None:#如果轮廓不为空(if contour is not NONE)
            rect = cv2.minAreaRect(cnt_large)#最小外接矩形(the minimum bounding rectangle)
            box = np.int0(cv2.boxPoints(rect))#最小外接矩形的四个顶点(the four vertices of the minimum bounding rectangle)
            for i in range(4):
                box[i, 1] = box[i, 1] + (n - 1)*roi_h + roi[0][0]
                box[i, 1] = int(Misc.map(box[i, 1], 0, size[1], 0, img_h))
            for i in range(4):                
                box[i, 0] = int(Misc.map(box[i, 0], 0, size[0], 0, img_w))
                
            cv2.drawContours(img_draw, [box], -1, (0,0,255,255), 2)#画出四个点组成的矩形(draw the rectangle formed by the four points)
        
            #获取矩形的对角点(retrieve the diagonal points of the rectangle)
            pt1_x, pt1_y = box[0, 0], box[0, 1]
            pt3_x, pt3_y = box[2, 0], box[2, 1]            
            center_x, center_y = (pt1_x + pt3_x) / 2, (pt1_y + pt3_y) / 2#中心点(center point)
            cv2.circle(img_draw, (int(center_x), int(center_y)), 5, (0,0,255), -1)#画出中心点(draw center point)
            
            center_.append([center_x, center_y])                        
            #按权重不同对上中下三个中心点进行求和(sum the weighted centroids of the upper, middle, and lower regions with different weights)
            centroid_x_sum += center_x * r[4]
            weight_sum += r[4]

    if weight_sum != 0:
        #求最终得到的中心点(calculate the final obtained center point)
        line_centerx = int(centroid_x_sum / weight_sum)
        cv2.circle(img_draw, (line_centerx, int(center_y)), 10, (0,255,255), -1)#画出中心(draw center)
    else:
        line_centerx = 8888

    return line_centerx


# 色块定位视觉处理函数(the visual processing function for color block localization)
def color_identify(img, img_draw, target_color = 'blue'):
    
    img_w = img.shape[:2][1]
    img_h = img.shape[:2][0]
    img_resize = cv2.resize(img, (size[0], size[1]), interpolation = cv2.INTER_CUBIC)
    GaussianBlur_img = cv2.GaussianBlur(img_resize, (3, 3), 0)#高斯模糊(Gaussian blur)
    frame_lab = cv2.cvtColor(GaussianBlur_img, cv2.COLOR_BGR2LAB) #将图像转换到LAB空间(convert the image to LAB space)
    frame_mask = cv2.inRange(frame_lab,
                                 (lab_data[target_color]['min'][0],
                                  lab_data[target_color]['min'][1],
                                  lab_data[target_color]['min'][2]),
                                 (lab_data[target_color]['max'][0],
                                  lab_data[target_color]['max'][1],
                                  lab_data[target_color]['max'][2]))  #对原图像和掩模进行位运算(perform bitwise operation to original image and mask)
    opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))#开运算(opening operation)
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))#闭运算(closing operation)
    contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2] #找出所有外轮廓(find out all the bounding contours)
    areaMax_contour = getAreaMaxContour(contours, area_min=50)[0] #找到最大的轮廓(find out the contour with the maximal area)

    left_x, right_x, center_y, angle = -1, -1, -1, 0
    if areaMax_contour is not None:
        down_x = (areaMax_contour[areaMax_contour[:,:,1].argmax()][0])[0]
        down_y = (areaMax_contour[areaMax_contour[:,:,1].argmax()][0])[1]

        left_x = (areaMax_contour[areaMax_contour[:,:,0].argmin()][0])[0]
        left_y = (areaMax_contour[areaMax_contour[:,:,0].argmin()][0])[1]

        right_x = (areaMax_contour[areaMax_contour[:,:,0].argmax()][0])[0]
        right_y = (areaMax_contour[areaMax_contour[:,:,0].argmax()][0])[1]
        
        if pow(down_x - left_x, 2) + pow(down_y - left_y, 2) > pow(down_x - right_x, 2) + pow(down_y - right_y, 2):
            left_x = int(Misc.map(left_x, 0, size[0], 0, img_w))
            left_y = int(Misc.map(left_y, 0, size[1], 0, img_h))  
            right_x = int(Misc.map(down_x, 0, size[0], 0, img_w))
            right_y = int(Misc.map(down_y, 0, size[1], 0, img_h))
        else:
            left_x = int(Misc.map(down_x, 0, size[0], 0, img_w))
            left_y = int(Misc.map(down_y, 0, size[1], 0, img_h))
            right_x = int(Misc.map(right_x, 0, size[0], 0, img_w))
            right_y = int(Misc.map(right_y, 0, size[1], 0, img_h))

        center_y = int(Misc.map((areaMax_contour[areaMax_contour[:,:,1].argmax()][0])[1], 0, size[1], 0, img_h))
        angle = int(math.degrees(math.atan2(right_y - left_y, right_x - left_x)))
        
        cv2.line(img_draw, (left_x, left_y), (right_x, right_y), (255, 0, 0), 2)     
            
    return left_x, right_x, center_y, angle      


skip = 1
skip_st = True
items = None
line_st = True
fence_st = True
strp_up = True
x_center = 360
#机器人跟踪线程(robot tracking thread)
def move():
    global object_center_y,line_centerx,items
    global line_st,strp_up,fence_st,skip_st
    
    while True:
        if switch:
            if object_center_y >= 300:  #检测到台阶或者跨栏,进行位置微调(detect steps or hurdles and perform position refinement)
                
                if 20 <= object_angle < 90:
                    AGC.runActionGroup(go_turn_right)
                    time.sleep(0.2)           
                elif -20 >= object_angle > -90:
                    AGC.runActionGroup(go_turn_left)
                    time.sleep(0.2)
                
                elif line_centerx - x_center > 15:
                    AGC.runAction(right_move)
                elif line_centerx - x_center < -15:
                    AGC.runAction(left_move)
                
                elif 3 < object_angle < 20:
                    AGC.runActionGroup(turn_right)
                    time.sleep(0.2)           
                elif -5 > object_angle > -20:
                    AGC.runActionGroup(turn_left)
                    time.sleep(0.2)
                    
                elif 300 <= object_center_y < 430:    #在中心(in the center)
                    AGC.runActionGroup(go_forward_one_step)
                    time.sleep(0.2)
                    
                elif object_center_y >= 430: #位置靠近，可以跨栏或者上下台阶(the positions are close, allowing for stepping over or stepping onto/down from the platform)
                    time.sleep(0.5)
                    if object_center_y >= 430:
                        board.set_buzzer(1900, 0.1, 0.9, 1)
                        AGC.runActionGroup(go_forward_one_step) #前进一步(take one step forward)
                        time.sleep(0.5)
                        AGC.runActionGroup(go_forward_one_step) #前进一步(take one step forward)
                        time.sleep(0.5)
                        
                        if items == 'hurdles':# 跨栏(hurdles)
                            
                            AGC.runActionGroup('hurdles')
                            skip_st = True
                            strp_up = True
                            items = None
                        elif items == 'stairway':
                            if strp_up: # 上台阶(go up stairs)
                                AGC.runActionGroup('climb_stairs')
                                strp_up = False
                            else: # 下台阶(go down stairs)
                                for i in range(2):
                                    AGC.runActionGroup(go_forward_one_step)
                                time.sleep(0.2)
                                AGC.runActionGroup('down_floor')
                                strp_up = True
                            items = None
                            skip_st = True
                        time.sleep(0.5)
                        object_center_y = -1
                    
                else:
                    time.sleep(0.01)
                    
            elif line_st and line_centerx != 8888: #巡线(line following)
                if abs(line_centerx - x_center) <= 20:
                    AGC.runAction(go_forward)
                    time.sleep(0.2)
                elif line_centerx - x_center > 20:
                    AGC.runAction(go_turn_right)
                    time.sleep(0.2)
                elif line_centerx - x_center < -20:
                    AGC.runAction(go_turn_left)
                    time.sleep(0.2)
                else:
                    time.sleep(0.01)
            else:
                time.sleep(0.01)
        else:
            time.sleep(0.01)
                
            
#作为子线程开启(start as a sub-thread)
th = threading.Thread(target=move)
th.daemon = True
th.start()


def run(img):
    global skip_st, line_st, strp_st, fence_st
    global object_left_x, object_right_x, skip, items
    global object_center_y, object_angle, line_centerx
    
    img_copy = img.copy()
    img_h, img_w = img.shape[:2]
    
    # 巡线(line following)
    line_centerx = line_patrol(img, img_copy, target_color = 'black') 
    
    # 跨栏(hurdles)
    if skip == 1:
        object_left_x, object_right_x, object_center_y, object_angle = color_identify(img, img_copy, target_color = 'blue')
        print('hurdles',object_left_x, object_right_x, object_center_y, object_angle)# 打印位置角度参数(print position angle parameter)
        if object_center_y >= 260:#准备跨栏，关闭错帧检测(prepare for hurdles, disable error frame detection)
            skip_st = False
            items = 'hurdles'
        elif object_center_y == -1:
            skip_st = True

    # 台阶(stair)
    elif skip == 2:
        object_left_x, object_right_x, object_center_y, object_angle = color_identify(img, img_copy, target_color = 'red')
        print('stairway',object_left_x, object_right_x, object_center_y, object_angle)# 打印位置角度参数(print position angle parameter)
        if object_center_y >= 260:#准备上台阶，关闭错帧检测(prepare to ascend stairs, disable error frame detection)
            skip_st = False
            items = 'stairway'
        elif object_center_y == -1:
            skip_st = True
               
    if skip_st: # 设置跨栏和台阶错帧检测(enable error frame detection for hurdles and stairs)
        skip += 1 
        if skip > 2:
            skip = 1
        
    return img_copy

if __name__ == '__main__':
    
    from hiwonder.CalibrationConfig import *
    init()   
    
    #加载参数(load parameters)
    param_data = np.load(calibration_param_path + '.npz')
    mtx = param_data['mtx_array']
    dist = param_data['dist_array']
    newcameramtx, roi_area = cv2.getOptimalNewCameraMatrix(mtx, dist, (640, 480), 0, (640, 480))
    mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (640, 480), 5)

    
    camera = cv2.VideoCapture(-1)
    AGC.runAction('stand_slow')
    switch = True
    while True:
        ret,img = camera.read()
        if ret:
            frame = img.copy()
            frame = cv2.remap(frame.copy(), mapx, mapy, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
            
            Frame = run(frame)           
            # cv2.imshow('Frame', Frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    camera.camera_close()
    cv2.destroyAllWindows()

