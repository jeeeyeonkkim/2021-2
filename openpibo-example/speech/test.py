import pyttsx3 as pt
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
from speech.speechlib import cSpeech
from audio.audiolib import cAudio


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
from speech.speechlib import cDialog



def tts_f(msg,num,voice):
  tObj = cSpeech(conf=cfg)
  filename = cfg.TESTDATA_PATH+"/test.mp3"
  tObj.tts("<speak>\
              <voice name='WOMAN_READ_CALM'>"+msg+"<break time='500ms'/></voice>\
            </speak>"\
          , filename)
  print(filename)
  aObj = cAudio()
  aObj.play(filename, out='local', volume=voice)
  time.sleep(num)

def speech(msg,num,v):
    filename = cfg.TESTDATA_PATH+"/"+msg+".mp3"
    aObj.play(filename, out='local', volume=v)
    time.sleep(num)

tts_f("안녕하세요 반갑습니다. ", 1, 60)

