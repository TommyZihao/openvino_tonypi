# 录音+语音识别
# 同济子豪兄 2024-9-7

# 查看麦克风索引号
# arecord -l

# 录音
def record(MIC_INDEX=3, DURATION=6):
    '''
    调用麦克风录音，需用arecord -l命令获取麦克风ID
    DURATION，录音时长
    '''
    print('开始 {} 秒录音'.format(DURATION))
    os.system('sudo arecord -D "plughw:{}" -f dat -c 1 -r 16000 -d {} /home/pi/TonyPi/OpenVINO/temp/speech_record.wav'.format(MIC_INDEX, DURATION))
    print('录音结束')

import wave
import numpy as np
import os
import sys

# 语音识别
import os
import appbuilder
# 配置密钥
os.environ["APPBUILDER_TOKEN"] = "bce-v3/ALTAK-2vgbNGzJ3OVmoozGS5frf/b4678ea066b57b348ca14faa92addc65a53d77b9"
asr = appbuilder.ASR() # 语音识别组件

def speech_recognition(audio_path='/home/pi/TonyPi/OpenVINO/temp/speech_record.wav'):
    '''
    AppBuilder-SDK语音识别组件
    '''
    print('开始语音识别')
    # 载入wav音频文件
    with wave.open(audio_path, 'rb') as wav_file:
        
        # 获取音频文件的基本信息
        num_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        framerate = wav_file.getframerate()
        num_frames = wav_file.getnframes()
        
        # 获取音频数据
        frames = wav_file.readframes(num_frames)
        
    # 向API发起请求
    content_data = {"audio_format": "wav", "raw_audio": frames, "rate": 16000}
    message = appbuilder.Message(content_data)
    speech_result = asr.run(message).content['result'][0]
    # print('语音识别结果：', speech_result)

    speech_recognition_txt = '/home/pi/TonyPi/OpenVINO/temp/speech_recognition.txt'
    with open(speech_recognition_txt, 'w') as f:
        f.write(speech_result)
        # print('语音识别结果已写入txt文件')

    return speech_result

record()
speech_recognition()
# print('完成录音+语音识别')