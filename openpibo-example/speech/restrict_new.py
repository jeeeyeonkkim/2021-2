#!/usr/bin/python
# >>stt
'''
set GOOGLE_APPLICATION_CREDENTIALS=C:/home/pi/Downloads/vast-verve-320303-b594822e4a04.json
export GOOGLE_APPLICATION_CREDENTIALS="/home/pi/Downloads/vast-verve-320303-b594822e4a04.json"
'''
# set GOOGLE_APPLICATION_CREDENTIALS=C:/home/pi/Downloads/vast-verve-320303-b594822e4a04.json

# gcloud auth activate-service-account --key-file="/home/pi/Downloads/vast-verve-320303-b594822e4a04.json"

# export GOOGLE_APPLICATION_CREDENTIALS="/home/pi/Downloads/vast-verve-320303-b594822e4a04.json"

# >>tts

# vast-verve-320303-5b57752cb55a // .json

# /home/pi/Downloads/vast-verve-320303-5b57752cb55a.json

# 가상환경 활성화 source test/bin/activate

from __future__ import division

import pandas as pd
import threading
import alsaaudio
import pyaudio
import pyttsx3
import socket
import numpy
import time
import pygame
import sys
import cv2
import ast
import re
import os
import gspeech
from google.cloud import speech
from six.moves import queue

# 상위 디렉토리 추가 (for utils.config)
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg

sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from vision.visionlib import cCamera
from motion.motionlib import cMotion
from audio.audiolib import cAudio
from oled.oledlib import cOled
from speech.speechlib import cSpeech
from speech.speechlib import cDialog

oObj = cOled(conf=cfg)
m = cMotion(conf=cfg)
'''
def playSound(filename):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

def tts_f():
    pygame.mixer.init()
    playSound('5m.mp3')
    time.sleep(30.0)
'''
data_pd = pd.read_excel('/home/pi/openpibo-data/proc/dialog.xls', header = None) # names = ['명령어', '대답', '종료여부', '모션'])
cmdLists = pd.DataFrame.to_numpy(data_pd)

# 이거 안 씀 motion_flag = 0 # 모션 동작 연속적으로 할 수 있게 하는 flag
# 이거 안 씀 count_flag = 0
# 이거 안 씀 wait = 0

###변수 선언부###
status_speak_mode = 2 # 전역 / 안내모드  : 1, 일상모드 : 0 / cmdLists[i][3] 2: 대기모드
flag_action = 0
motion_once = 0
r_arm = -70
r_hand = -25
l_arm = 70
l_hand = 25

R_ARM_P = 8
R_ARM_D = 0.05
repeat = 0 # 안내모드 시 순차적 동작 실행하는데 쓰임 

r_arm_p = R_ARM_P # 파이보 모션 제어 
r_arm_d = R_ARM_D
l_arm_p = R_ARM_P
r_hand_p = 4
l_hand_p = r_hand_p
r_hand_d = 1

global_vol = 0

def speak(msg,num,voice):
    tObj = cSpeech(conf=cfg)
    filename = cfg.TESTDATA_PATH+"/test.mp3"
    print("voice : ", voice)
    tObj.tts("<speak>\
                <voice name='WOMAN_READ_CALM'>"+msg+"<break time='500ms'/></voice>\
                </speak>"\
            , filename)
    aObj = cAudio()
    # audio.setvolume(voice)
    # current_volume = audio.getvolume() # Get the current Volume
    # print("current_volume :", current_volume)

    aObj.play(filename, out='local', volume=global_vol)
    time.sleep(num)
    
def CommandProc(stt):
    global flag_action, repeat
    global status_speak_mode, global_vol
    # 문자 양쪽 공백 제거
    cmd = stt.strip()
    # 입력 받은 문자 화면에 표시
    
    print('나 : ' + str(cmd))
    for i in range(len(cmdLists)):
        if cmdLists[i][0] in str(cmd):
             
            status_speak_mode = int(cmdLists[i][3]) 
            print ('구글 스피치 : ' + cmdLists[i][1])
            print("global_vol : ", global_vol)
            speak(cmdLists[i][1], len(cmdLists[i][1])/5, global_vol)
            
            
            print("\n>>말해주세요~")
            print("cmdLists[i][3] : ", cmdLists[i][3])
            gsp.resumeMic()
            return cmdLists[i][2]
    # 리스트에 없는 명령어일 경우 
    print ('구글 스피치 : 무슨 얘기하는 거니?')
    speak('무슨이야기 하는거니?', 1, global_vol)
    status_speak_mode = 2
    time.sleep(2)
    gsp.resumeMic()
    print("\n>>말해주세요~")
    return 1



def eye_tracking(r_arm, r_hand, motionData_x, motionData_y, l_arm, l_hand):
    MT = 300
    
    global flag_action, motion_once
    global status_speak_mode
    # print("------------")
    # print("status_speak_mode(tracking): ", status_speak_mode)
    
    if status_speak_mode == 1 and motion_once == 0 : # 안내모드 일 때 
        motion_once += 1
        oObj.draw_image(cfg.TESTDATA_PATH +"/i2.JPEG")
        oObj.show() # oled 띄우는 것 
        m.set_motion(name="guide2", cycle=1)
        motion_once = 0
        status_speak_mode = 2
  
        
    elif status_speak_mode == 0 and motion_once == 0 : # 일상모드 일 떄 
        motion_once += 1
        oObj.draw_image(cfg.TESTDATA_PATH +"/conversation.png")
        oObj.show() # oled 띄우는 것 
        m.set_motion(name="clapping2", cycle=1)
        motion_once = 0
        status_speak_mode = 2

    elif status_speak_mode == 2: # 음성 입력 없을 때 그냥 트래킹만 하는 것. 숨쉬기 모드 
        # print("r_hand, l_hand: ", r_hand, l_hand)
        m.set_motors(positions=[0,0,-70,r_hand, motionData_x, motionData_y,0,0,70,l_hand], movetime=MT) 
        oObj.draw_image(cfg.TESTDATA_PATH +"/pibo_logo.png") 
        oObj.show() # oled 띄우는 것 
    
            
"""구글 스피치 부분 함수 끝"""

#연결할 서버(수신단)의 ip주소와 port번호
TCP_IP = '192.168.0.79'
TCP_PORT = 5001
#송신을 위한 socket 준비
sock = socket.socket()
sock.connect((TCP_IP,TCP_PORT))
#OpenCV를 이용해서 webcam으로 부터 이미지 추출

capture = cv2.VideoCapture(0)

m.set_motors(positions=[0,0,-70,-25,0,0,0,0,70,25], movetime=500)

time.sleep(3)
motion_list = []

audio = alsaaudio.Mixer()
current_volume = audio.getvolume() # Get the current Volume
audio.setvolume(30) # Set the volume to 70%.

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

text = pyttsx3.init()

'''
# 말하는 속도
text.setProperty('rate', 150)
rate = text.getProperty('rate')
# 목소리
voices = text.getProperty('voices')
# text.setProperty('voice', voices[0].id) # 남성
text.setProperty('voice', 'english+f1') # 여성
# text.setProperty('voice', voices[1].id) # 여성
'''

gsp = gspeech.Gspeech()
def main():    
    while True:
        # 음성 인식 될때까지 대기 한다.
        stt = gsp.getText()
        if stt is None:
            break
        gsp.pauseMic()
        time.sleep(0.01)
        CommandProc(stt)

        #끝내자는 명령이 들어오면 프로그램 종료
        if ('끝내자' in stt):
            break
        
STT = threading.Thread(target = main) # 구글 스피치 thread  
STT.start()
while True :
    
    ret, frame = capture.read()
    frame = cv2.flip(frame,0)

    #추출한 이미지를 String 형태로 변환(인코딩)시키는 과정
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
    result, imgencode = cv2.imencode('.jpg', frame, encode_param)
    data = numpy.array(imgencode)
    stringData = data.tostring()

    #String 형태로 변환한 이미지를 socket을 통해서 전송
    sock.send( str(len(stringData)).ljust(16).encode())
    sock.send( stringData )

    # 파이보로부터 motion data 수신했는지 판단 여부
    people = sock.recv(1).decode("utf8")
    # print("motion_send : ", people)

    if people != '0' and people != '':
        
        # 파이보로부터 Motion data 수신
        motion_list = sock.recv(1024)
        # print("motion_list : ", motion_list)
        motion_list = eval(motion_list)
        motionData_x = int(motion_list[0])
        motionData_y = int(motion_list[1])
        vol = int(motion_list[2])
        global_vol = vol
        motion_list = []
        
        if status_speak_mode == 2 : 
            # 숨쉬는 귀여운 파이보 가만히 있을 때 
            if l_hand < -20 or l_hand > 25 :
                l_hand_p = -1 * l_hand_p
            # print(">>l_hand_p :", l_hand_p)
            l_hand -= l_hand_p
            r_hand = -1 * l_hand
        

        eye_track = threading.Thread(target=eye_tracking, args=(r_arm, r_hand, motionData_x, motionData_y, l_arm, l_hand))
        eye_track.start()
    else :
        if status_speak_mode == 2 : 
            # 숨쉬는 귀여운 파이보 가만히 있을 때 
            if l_hand < -20 or l_hand > 25 :
                l_hand_p = -1 * l_hand_p
            # print(">>l_hand_p :", l_hand_p)
            l_hand -= l_hand_p
            r_hand = -1 * l_hand

            eye_track = threading.Thread(target=eye_tracking, args=(r_arm, r_hand, 0, 0, l_arm, l_hand))
            eye_track.start()
        
cv2.destroyAllWindows() 
sock.close()
