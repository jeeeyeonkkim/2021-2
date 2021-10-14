#!/usr/bin/python
# >>stt

# set GOOGLE_APPLICATION_CREDENTIALS=C:/home/pi/Downloads/vast-verve-320303-b594822e4a04.json

# gcloud auth activate-service-account --key-file="/home/pi/Downloads/vast-verve-320303-b594822e4a04.json"

# export GOOGLE_APPLICATION_CREDENTIALS="/home/pi/Downloads/vast-verve-320303-b594822e4a04.json"

# source ~/speech/env/bin/activate

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

from google.cloud import speech
from six.moves import queue

# 상위 디렉토리 추가 (for utils.config)
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg
# openpibo 라이브러리 경로 추가
sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from vision.visionlib import cCamera
# openpibo 라이브러리 경로 추가
sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from motion.motionlib import cMotion
# openpibo 라이브러리 경로 추가
sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from audio.audiolib import cAudio
# openpibo 라이브러리 경로 추가
sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from oled.oledlib import cOled
# openpibo 라이브러리 경로 추가
sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from speech.speechlib import cDialog

def playSound(filename):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

def tts_f():
    pygame.mixer.init()
    playSound('5m.mp3')
    time.sleep(30.0)

status_speak_mode = 0 # 전역 / 안내모드  : 1, 일상모드 : 0 / cmdLists[i][3]

data_pd = pd.read_excel('/home/pi/openpibo-data/proc/dialog.xls', header = None) # names = ['명령어', '대답', '종료여부', '모션'])
cmdLists = pd.DataFrame.to_numpy(data_pd)

oObj = cOled(conf=cfg)
m = cMotion(conf=cfg)

"""구글 스피치 부분 함수 및 클래스 시작"""

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)
# [END audio_stream]

def CommandProc(stt):
    # 문자 양쪽 공백 제거
    cmd = stt.strip()
    # 입력 받은 문자 화면에 표시
    print('나 : ' + str(cmd))
    for i in range(len(cmdLists)):
        if cmdLists[i][0] in str(cmd):
            global status_speak_mode 
            status_speak_mode = int(cmdLists[i][3]) # a == status_speak_mode
            print ('구글 스피치 : ' + cmdLists[i][1])
            
            text.say(cmdLists[i][1])
            text.runAndWait()
            # 다시 원 자세로 복귀
            # m.set_motion(name="stop", cycle=1)
            
            print("\n>>말해주세요~")
            print("cmdLists[i][3] : ", cmdLists[i][3])
            
            return cmdLists[i][2]
    # 리스트에 없는 명령어일 경우 
    print ('구글 스피치 : 무슨 얘기하는 거냐!?')
    text.say('무슨 얘기하는 거냐!?')
    text.runAndWait()
    print("\n>>말해주세요~")
    return 1
flag_action = 0
motion_flag = 0 # 모션 동작 연속적으로 할 수 있게 하는 flag
r_arm = -70
r_hand = -25
def eye_tracking(r_arm, r_hand, motionData_x, motionData_y):
    MT = 1000
    
    global flag_action
    global status_speak_mode
    # print("------------")
    # print("status_speak_mode(tracking): ", status_speak_mode)
    
    if status_speak_mode == 1 : # 안내모드 일 때 
        flag_action = 1
        print("flag_action(eye tracking) :", flag_action)
        oObj.draw_image(cfg.TESTDATA_PATH +"/conversation.png")
        oObj.show() # oled 띄우는 것 
        m.set_motors(positions=[ 0, 0, r_arm, r_hand, motionData_x, motionData_y, 0, 0, 30, 25 ], movetime=MT)
    elif status_speak_mode == 0 : # 일상모드 일 떄 (status_speak_mode = 0 )
        oObj.draw_image(cfg.TESTDATA_PATH +"/clear.png") 
        oObj.show() # oled 띄우는 것 
        m.set_motors(positions=[0,0,-70,-25, motionData_x, motionData_y,0,0,70,25], movetime=MT)
    elif status_speak_mode == 2: # 음성 입력 없을 때 그냥 트래킹만 하는 것.
        oObj.clear()
        m.set_motors(positions=[0,0,-70,-25, motionData_x, motionData_y,0,0,70,25], movetime=MT)

def listen_print_loop(responses):
    """
    https://goo.gl/tjCPAU.
    """
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        # There could be multiple results in each response.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if not result.is_final:
            ### 추가 ### 화면에 인식 되는 동안 표시되는 부분.
            sys.stdout.write('나 : ')
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()
            num_chars_printed = len(transcript)

        else:
            ### 추가 ### 
            if CommandProc(transcript) == 0:
                break
            num_chars_printed = 0

# 
# def start_move(mot):
#     if mot == '0': # 일상 대화 제스처 
#         do ='clapping2'
#         oObj.draw_image(cfg.TESTDATA_PATH +"/clear.png")
#         oObj.show()
#     else:
#         do ='guide1' # 안내 제스처 오른쪽 팔 
#         oObj.draw_image(cfg.TESTDATA_PATH +"/conversation.png")
#         oObj.show()
#     m.set_motion(name=do, cycle=1)
#     oObj.clear()

# def stop_move():
#     m.set_motion(name="stop", cycle=1)

"""구글 스피치 부분 함수 끝"""

#연결할 서버(수신단)의 ip주소와 port번호
TCP_IP = '192.168.0.76'
TCP_PORT = 5001
#송신을 위한 socket 준비
sock = socket.socket()

sock.connect((TCP_IP,TCP_PORT))
#OpenCV를 이용해서 webcam으로 부터 이미지 추출

capture = cv2.VideoCapture(0)

m.set_motors(positions=[0,0,-70,-25,0,0,0,0,70,25], movetime=5000)
time.sleep(3)
motion_list = []

audio = alsaaudio.Mixer()
current_volume = audio.getvolume() # Get the current Volume
audio.setvolume(30) # Set the volume to 70%.

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
text = pyttsx3.init()

def main():
    language_code = 'ko-KR'  # 한국어로 변경 See http://g.co/cloud/speech/docs/languages
    
    client = speech.SpeechClient() # 클라이언트 구성 
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = speech.StreamingRecognitionConfig(
        config=config, # single_utterance = True, # 음성이 더 이상 감지되지 않으면 stt요청을 자동으로 종료
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (speech.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses)


STT = threading.Thread(target = main) # 구글 스피치 thread  
STT.start()

repeat = 0
r_arm_p = 6 # 파이보 모션 제어 
r_arm_d = 1.2
r_hand_p = 4
r_hand_d = 1
count_flag = 0
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

    if people != '0' :
        
        # 파이보로부터 Motion data 수신
        motion_list = sock.recv(1024)
        # print("motion_list : ", motion_list)
        motion_list = eval(motion_list)
        motionData_x = int(motion_list[0])
        motionData_y = int(motion_list[1])
        vol = int(motion_list[2])
        motion_list = []
        count_flag+=1
        print("repeat(main): ", repeat)
        # print("r_hand(main): ", r_hand)
        print("flag_action(main):", flag_action)

        if count_flag > 80:
            status_speak_mode = 2 # 아무것도 안 하는 모드 
            repeat = 0
            flag_action = 0
            r_arm = -70
            r_arm_d = 1.2
            r_arm_p = 6
            r_hand = -25
            r_hand_p = 4
            r_hand_d = 1

            if r_arm > -50 and r_arm <30:
                r_arm_d += 0.1
                r_arm_p = r_arm_p * r_arm_d

            if r_arm > -50:
                r_arm -= r_arm_p

        if flag_action == 1:
            repeat = repeat + 1
            print(">>repeat(main): ", repeat)
            print(">>r_arm(main): ", r_arm)

            if r_arm > -50 and r_arm <30:
                r_arm_d += 0.1
                r_arm_p = r_arm_p * r_arm_d

            if r_arm < 80:
                r_arm += r_arm_p
            
            if r_hand >= 8 or r_hand <-25: # 방향 바꾸는 것 
                r_hand_p = -1 * r_hand_p
            print("r_hand(main):", r_hand)
            print("r_hand_p(main):", r_hand_p)
            r_hand += r_hand_p
        
        eye_track = threading.Thread(target=eye_tracking, args=(r_arm, r_hand, motionData_x, motionData_y))
        eye_track.start()
        
        print("------------")
        
        
        audio.setvolume(vol)

cv2.destroyAllWindows() 
sock.close()