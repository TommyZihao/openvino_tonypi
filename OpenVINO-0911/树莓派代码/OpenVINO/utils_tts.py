# utils_tts.py
# 同济子豪兄 2024-5-23
# 语音合成

print('导入语音合成模块')

import sys
import os
import appbuilder

os.environ["APPBUILDER_TOKEN"] = "bce-v3/ALTAK-2vgbNGzJ3OVmoozGS5frf/b4678ea066b57b348ca14faa92addc65a53d77b9"

tts_ab = appbuilder.TTS()

def tts(TEXT='我是同济子豪兄的机器人', tts_wav_path = '/home/pi/TonyPi/OpenVINO/temp/tts.wav'):
    '''
    语音合成TTS，生成wav音频文件
    '''
    inp = appbuilder.Message(content={"text": TEXT})
    out = tts_ab.run(inp, model="paddlespeech-tts", audio_type="wav")
    # out = tts_ab.run(inp, audio_type="wav")
    with open(tts_wav_path, "wb") as f:
        f.write(out.content["audio_binary"])
    # print("TTS语音合成，导出wav音频文件至：{}".format(tts_wav_path))

def play_wav(wav_file='/home/pi/TonyPi/OpenVINO/temp/tts.wav'):
    '''
    播放wav音频文件
    '''
    prompt = 'aplay -t wav {} -q'.format(wav_file)
    os.system(prompt)

print('TTS Start')
with open('/home/pi/TonyPi/OpenVINO/temp/ai_response.txt', 'r', encoding='utf-8') as f:
    ai_response = f.read()
tts(ai_response)
play_wav()