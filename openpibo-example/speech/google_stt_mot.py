# -*- coding: utf-8 -*-
#!/usr/bin/env python

#
#      http://www.apache.org/licenses/LICENSE-2.0
#


# Google Cloud Speech API sample application using the streaming API.

# NOTE: This module requires the additional dependency `pyaudio`. To install
# using pip:

#     pip install pyaudio

# Example usage:
#     python transcribe_streaming_mic.py

# >>stt

# set GOOGLE_APPLICATION_CREDENTIALS=C:/home/pi/Downloads/vast-verve-320303-b594822e4a04.json

# gcloud auth activate-service-account --key-file="/home/pi/Downloads/vast-verve-320303-b594822e4a04.json"

# export GOOGLE_APPLICATION_CREDENTIALS="/home/pi/Downloads/vast-verve-320303-b594822e4a04.json"

# source ~/speech/env/bin/activate

# >>tts

# vast-verve-320303-5b57752cb55a // .json

# /home/pi/Downloads/vast-verve-320303-5b57752cb55a.json

# 가상환경 활성화 source test/bin/activate

# [START import_libraries]
from __future__ import division

import re
import sys
import os
from google.cloud import speech

from six.moves import queue
import pyaudio
import threading
import time
import pyttsx3
import pandas as pd

# 상위 디렉토리 추가 (for utils.config)
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg
# openpibo 라이브러리 경로 추가
sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from speech.speechlib import cDialog
# openpibo 라이브러리 경로 추가
sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from motion.motionlib import cMotion
# openpibo 라이브러리 경로 추가
sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from oled.oledlib import cOled

# [END import_libraries]

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
text = pyttsx3.init()
 
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

data_pd = pd.read_excel('/home/pi/openpibo-data/proc/dialog.xls', header = None) # names = ['명령어', '대답', '종료여부', '모션'])
cmdLists = pd.DataFrame.to_numpy(data_pd)
# cmdLists = [
#         #명령어    대답    종료 리턴값(모션)
#         [u'끝내자', '잘가라', 0, 0],
#         [u'안녕', '반가워 난 인공지능이야', 1, 0],
#         [u'레이 원', '잘생겼다', 1, 0],
#         [u'어제 뭐 했어', '치킨먹고 게임했어', 1, 0],
#         [u'티비는', '엘쥐', 1, 0],
#         [u'스마트폰은', '갤럭시', 1, 0],
#         [u'위치', '설명한다', 1, 1] # 6
#         ]
### 내일 키워드 들어오면 인식하는걸로 수정 (해결)

### 몇 초 기다렸다가 대답하는지 확인 (초는 정확히 찾을 수 없으나 음성 입력이 없으면 종료됨.) (해결)

# 안내 키워드 제스처 "그림", "위치" (해결)

# 일상대화 제스처 (해결)

# 설명하는 제스처 motion_db.json -> guide

"""
리턴이 0이면 종료
"""
def CommandProc(stt):
    # 문자 양쪽 공백 제거
    cmd = stt.strip()
    # 입력 받은 문자 화면에 표시
    print('나 : ' + str(cmd))

    for i in range(len(cmdLists)):
        if cmdLists[i][0] in str(cmd):
            
            a = int(cmdLists[i][3])
            a = str(a)
            print(a)
            # t1 = threading.Thread(target = start_move, args=a)
            # t1.start()
            threading.Thread(target = start_move, args = a).start()
            print ('구글 스피치 : ' + cmdLists[i][1])
            text.say(cmdLists[i][1])
            text.runAndWait()
            m.set_motion(name="stop", cycle=1)
            print("\n>>말해주세요~")
            return cmdLists[i][2]

    # 명령이 없으면
    print ('구글 스피치 : 무슨 얘기하는 거냐!?')
    text.say('무슨 얘기하는 거냐!?')
    text.runAndWait()
    print("\n>>말해주세요~")
    return 1
    
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
            
def start_move(mot):
    if mot == '0': # 일상 대화 제스처 
        do ='clapping2'
        oObj.draw_image(cfg.TESTDATA_PATH +"/clear.png")
        oObj.show()
    else:
        do ='guide1' # 안내 제스처 오른쪽 팔 
        oObj.draw_image(cfg.TESTDATA_PATH +"/conversation.png")
        oObj.show()
    m.set_motion(name=do, cycle=1)
    oObj.clear()

def stop_move():
    m.set_motion(name="stop", cycle=1)

def main():
    # See http://g.co/cloud/speech/docs/languages
    language_code = 'ko-KR'  # 한국어로 변경
    # obj = cDialog(conf=cfg)########
    # m = cMotion(conf=cfg)##########
    
    # 클라이언트 구성 
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        # single_utterance = True, # 음성이 더 이상 감지되지 않으면 stt요청을 자동으로 종료
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (speech.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses)


if __name__ == '__main__':
    print("시작")

    m = cMotion(conf=cfg)
    oObj = cOled(conf=cfg)
    # main()
    TT = threading.Thread(target = main)
    TT.start()
    print("여기부터 진짜 시작")