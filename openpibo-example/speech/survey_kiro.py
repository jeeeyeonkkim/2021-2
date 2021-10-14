#!/usr/bin/python
# >>stt
'''
set GOOGLE_APPLICATION_CREDENTIALS=C:/home/pi/Downloads/vast-verve-320303-b594822e4a04.json
export GOOGLE_APPLICATION_CREDENTIALS="/home/pi/Downloads/vast-verve-320303-b594822e4a04.json"
'''
# set GOOGLE_APPLICATION_CREDENTIALS=C:/home/pi/Downloads/vast-verve-320303-b594822e4a04.json

# gcloud auth activate-service-account --key-file="/home/pi/Downloads/vast-verve-320303-b594822e4a04.json"

# export GOOGLE_APPLICATION_CREDENTIALS="/home/pi/Downloads/vast-verve-320303-b594822e4a04.json"

# >>tts python3 restrict_repeat_and_q.py 

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

data_pd = pd.read_excel('/home/pi/openpibo-data/proc/dialog.xls', header = None) # names = ['명령어', '대답', '종료여부', '모션'])
cmdLists = pd.DataFrame.to_numpy(data_pd)

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
flag_speak  = 0

gsp = gspeech.Gspeech()

def speak(msg,num,voice):
    tObj = cSpeech(conf=cfg)
    filename = cfg.TESTDATA_PATH+"/test.mp3"
    print("voice : ", voice)
    tObj.tts("<speak>\
                <voice name='WOMAN_READ_CALM'>"+msg+"<break time='500ms'/></voice>\
                </speak>"\
            , filename)
    aObj = cAudio()

    aObj.play(filename, out='local', volume=-500)
    time.sleep(num)
    
def CommandProc(stt):
    global flag_action, repeat
    global status_speak_mode, global_vol, motion_repeat_num
    # 문자 양쪽 공백 제거
    cmd = stt.strip()
    # 입력 받은 문자 화면에 표시
    
    print('나 : ' + str(cmd))
    for i in range(len(cmdLists)):
        if '안녕' in str(cmd):
            status_speak_mode = 0 # 일상모드
            motion_repeat_num = int(round(89/20))-2 #여기 바꿔야함

            speak('안녕하세요 저 의 이름은 파이보 입니다. ', 3.5, global_vol) # 22 17 나누기 7
            gsp.resumeMic()
            
            speak('지금부터 제 소개를 할게요.\
             저는 반려로봇으로 개발 되었으며 휴먼로봇 인터렉션 연구에 적용되어 사용되고 있습니다.', 9, global_vol) # 66 50
            gsp.resumeMic()

            speak('그리고 전시관 안내로봇이 되어 개인화 서비스 제공을 목표로 사용될 예정입니다.', 6, global_vol) # 43 34
            gsp.resumeMic()
            status_speak_mode = 2
            return 1
        
        if '설명' in str(cmd):
            status_speak_mode = 1 # 안내모드
            motion_repeat_num = int(round(89/20))-2 # 여기 바꿔야함

            status_speak_mode = 10
            speak('저는 ssh를 통한 원격접속으로  프로그래밍을 하고, \
            소켓 전송을 통해 서버와  로컬에서 주고 받은 정보를 통해 작동됩니다,. \
            저는 처리해야할 연산량이 많기 때문에 , \
            실시간으로 카메라에서 찍은 사진을 local로 소켓으로 전송하고 데이터를 처리합니다.', 19, global_vol) 
            #왼쪽 팔 올리기 
            gsp.resumeMic()

            status_speak_mode = 11
            speak('사람 얼굴은 이렇게 인식합니다. . \
            face detection with mask 라는 딥러닝 모델을 이용하여, \
            카메라의 이미지에서 마스크를 쓴 사람과 쓰지 않은 사람을 구분하여 face tracking을 합니다. ', 14, global_vol)
            
            gsp.resumeMic()

            status_speak_mode = 12
            speak('사람의 얼굴을 보고 눈맞춤을 할 수 있습니다,.  .\
            이미지에서 tracking 하려는 사람의 boundary box 중심점의 x 좌표 와 . y 좌표를 구하여 \
            카메라에서의 중심점과의 차이점이  최소가 되도록 목 관절 모터를 제어합니다. . \
            이 때, 자연스러운 목 움직임을 만들기 위해 PD 제어가 적용되었습니다,. . .\
            P값과 D값을 통해 모터 속도를 높이는 방법으로 부드럽게 움직일 수 있습니다.', 28, global_vol) # 제스처 수정 여기 다리

            gsp.resumeMic()

            status_speak_mode = 13
            speak('저는 여러 사람과 눈맞춤을 할 수도 있습니다.  \
            여러 사람과 눈맞춤 하기 위해서, 이미지 내 boundary box가 가장 큰 사람을 tracking을 하거나, \
            화면 내 모든 boundary box의 중심점들의 중심점을 tracking을 합니다,. . \
            또는 이미지 내 사람들 중 일정 시간 간격으로 random하게 선택하여 tracking을 할 수도 있습니다,', 26, global_vol) # 시간 많이 줄이기 + 
            
            gsp.resumeMic()

            status_speak_mode = 14
            speak('여러분과 대화는 이렇게 할 수 있습니다. \
            저는 구글 클라우드 플랫폼의 stt-api를 이용해 사용자의 음성을 인식하고, \
            특정 단어를 인식해 대화 모델에서 알맞은 답변을 골라 대답할 수 있습니다. \
            대화를 위해서 3W 스피커와 MEMS 마이크를 사용합니다,,. \
            그리고 한사람과 대화할 경우,  boundary box의 크기를 이용해 speech volume을 조절하고, 여러 사람과 대화할 경우, \
            boundary box의 개수를 이용하여 speech volume을 조절합니다.', 34, global_vol) #사이클 줄이기 하나 시간 조금 줄이기
            
            gsp.resumeMic()
            
            status_speak_mode = 15
            speak('지금까지 제 소개를 했는데 어떠셨나요?  \
            제 소개를 듣고나서 받은 여러분의 인상을  제공해드린 설문에 응답해주시면 좋겠습니다. \
            안녕히 계세요.', 11, global_vol)
            gsp.resumeMic()
            return 1

    # 리스트에 없는 명령어일 경우 
    print ('구글 스피치 : 무슨 얘기하는 거니?')
    # speak('무슨이야기 하는거니?', 1, global_vol)
    status_speak_mode = 2
    time.sleep(2)
    gsp.resumeMic()
    print("\n>>말해주세요(그 외)")
    return 1

def eye_tracking(r_arm, r_hand, motionData_x, motionData_y, l_arm, l_hand):
    MT = 300
    
    global flag_action, motion_once, motion_repeat_num
    global status_speak_mode, flag_status
    # print("------------")
    # print("status_speak_mode(tracking): ", status_speak_mode)
    
    if status_speak_mode == 1 and motion_once == 0: # 안내모드 일 때 
        motion_once += 1
        oObj.draw_image(cfg.TESTDATA_PATH +"/i2.JPEG")
        oObj.show() # oled 띄우는 것 
        print("motion_repeat_num:",motion_repeat_num)
        
        m.set_motion(name="guide2", cycle=motion_repeat_num)
        gsp.resumeMic()
        m.set_motion(name="wake_up3", cycle=1)
        status_speak_mode = 2
        motion_once = 0
        
    elif status_speak_mode == 0 and motion_once == 0 : # 일상모드 일 떄 
        motion_once += 1
        oObj.draw_image(cfg.TESTDATA_PATH +"/conversation.png")
        oObj.show() # oled 띄우는 것 
        m.set_motion(name="greeting", cycle=3)
        m.set_motion(name="clapping2", cycle=2)
        motion_once = 0

    elif status_speak_mode == 2: # 음성 입력 없을 때 그냥 트래킹만 하는 것. 숨쉬기 모드 
        m.set_motors(positions=[0,0,-70,r_hand, motionData_x, motionData_y,0,0,70,l_hand], movetime=MT) 
        oObj.draw_image(cfg.TESTDATA_PATH +"/pibo_logo.png") 
        oObj.show() # oled 띄우는 것 

    elif status_speak_mode == 10 and motion_once == 0 : 
        motion_once += 1
        oObj.draw_image(cfg.TESTDATA_PATH +"/i2.JPEG")
        oObj.show() # oled 띄우는 것
        m.set_motion(name="speak_l2", cycle=2)
        motion_once = 0

    elif status_speak_mode == 11 and motion_once == 0 :
        motion_once += 1
        oObj.draw_image(cfg.TESTDATA_PATH +"/i2.JPEG")
        oObj.show() # oled 띄우는 것
        m.set_motion(name="guide2", cycle=4)
        motion_once = 0

    elif status_speak_mode == 12 and motion_once == 0 : # 사이클 한턴 더 길게
        motion_once += 1
        oObj.draw_image(cfg.TESTDATA_PATH +"/i2.JPEG")
        oObj.show() # oled 띄우는 것
        m.set_motion(name="wake_up3", cycle=2)
        m.set_motors(positions=[ 999, 999, 999, -25, 0, 0, 999, 999, 999,  25 ], movetime=500)

        motion_once = 0

    elif status_speak_mode == 13 and motion_once == 0 : 
        motion_once += 1
        oObj.draw_image(cfg.TESTDATA_PATH +"/i2.JPEG")
        oObj.show() # oled 띄우는 것
        m.set_motion(name="cheer3", cycle=3)
        motion_once = 0

    elif status_speak_mode == 14 and motion_once == 0 : 
        motion_once += 1
        oObj.draw_image(cfg.TESTDATA_PATH +"/i2.JPEG")
        oObj.show() # oled 띄우는 것
        m.set_motion(name="cheer4", cycle=2)
        motion_once = 0

    elif status_speak_mode == 15 and motion_once == 0 :
        motion_once += 1
        oObj.draw_image(cfg.TESTDATA_PATH +"/i2.JPEG")
        oObj.show() # oled 띄우는 것
        m.set_motion(name="welcome", cycle=2)
        m.set_motion(name="bow", cycle=1)
        m.set_motors(positions=[0,0,-70,-25,10,0,0,0,70,25], movetime=1000)
        
        status_speak_mode = 2
        motion_once = 0


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

# audio = alsaaudio.Mixer()
# current_volume = audio.getvolume() # Get the current Volume
# audio.setvolume(30) # Set the volume to 70%.

# Audio recording parameters
RATE = 22050
CHUNK = int(RATE / 10)  # 100ms

text = pyttsx3.init()
def main():    
    while True:
        # 음성 인식 될때까지 대기 한다.
        stt = gsp.getText()
        if stt is None:
            break
        gsp.pauseMic()
        # print("gsp_main : ", gsp.status)
        # gsp.status = Trues 여기 수정 했음 20210928
        # time.sleep(0.01)
        CommandProc(stt)

        #끝내자는 명령이 들어오면 프로그램 종료
        if ('끝내자' in stt):
            break
        
STT = threading.Thread(target = main) # 구글 스피치 thread  
STT.start()

global_motionData_x = 0
global_motionData_y = 0
while True :
    # speak('안녕하세요 저 의 이름은 파이보 입니다. ', 3.5, global_vol) # 22 17 나누기 7

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
        if status_speak_mode == 1 : # 안내 동작 후 고개 꺾이는 것 방지
            motionData_x = 0
            motionData_y = 0
            # print("gsp_repeat : ", gsp.status)
            
        
        elif status_speak_mode == 2 :
            # 숨쉬는 귀여운 파이보 가만히 있을 때
          
            if l_hand < -20 or l_hand > 25 :
                l_hand_p = -1 * l_hand_p
           
            l_hand -= l_hand_p
            r_hand = -1 * l_hand
            # print("motions x: ", motionData_x)
            # print("motions y: ", motionData_y)
        global_motionData_x = motionData_x
        global_motionData_y = motionData_y

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

            eye_track = threading.Thread(target=eye_tracking, args=(r_arm, r_hand, global_motionData_x, global_motionData_y, l_arm, l_hand))
            eye_track.start()
        
cv2.destroyAllWindows() 
sock.close()
