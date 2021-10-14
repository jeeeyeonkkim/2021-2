import os
import sys
import alsaaudio
import pygame
import time

# 상위 디렉토리 추가 (for utils.config)
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg

# openpibo 라이브러리 경로 추가
sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from audio.audiolib import cAudio

def playSound(filename):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

def tts_f():
    pygame.mixer.init()
    playSound('5m.mp3')
    time.sleep(4.0)

if __name__ == "__main__":
    tts_f()

# pygame.init()
