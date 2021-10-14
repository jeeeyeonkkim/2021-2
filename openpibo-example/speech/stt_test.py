import os
import sys
import re

# 상위 디렉토리 추가 (for utils.config)
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
#sys.path.append('/home/pi/openpibo-example/')
from utils.config import Config as cfg

# openpibo 라이브러리 경로 추가
sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from speech.speechlib import cSpeech

obj = cSpeech(conf=cfg)
ret = obj.stt(filename="stream.wav", timeout=5)
print(ret)
