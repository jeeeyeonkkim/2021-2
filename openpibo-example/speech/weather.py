import os
import sys
import threading

# 상위 디렉토리 추가 (for utils.config)
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg

# openpibo 라이브러리 경로 추가
sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from speech.speechlib import cSpeech
from audio.audiolib import cAudio
from motion.motionlib import cMotion

def moving():
  m = cMotion(conf=cfg)
  m.set_motion(name="wave3", cycle=1)
  # print(threading.currentThread().getName(), number)

def tts_f():
  tObj = cSpeech(conf=cfg)
  filename = cfg.TESTDATA_PATH+"/tts.mp3"
  tObj.tts("<speak>\
              <voice name='MAN_READ_CALM'>오늘 날씨 좋아요.<break time='500ms'/></voice>\
            </speak>"\
          , filename)
  print(filename)
  aObj = cAudio()
  aObj.play(filename, out='local', volume=-1500)

obj = cSpeech(conf=cfg)

#ret=결과..(성공/실패) 글자 받아서 한 글자씩 체크
ret = obj.stt()
test_string =  "".join(ret)

ex_1 = test_string.find('날')
ex_2 = test_string.find('씨')
# print(ex_1)
# print(ex_2)

if ex_1 >=-1 and ex_2 >= -1:
    print('존재함..')
    t = threading.Thread(target = moving)
    t.start()
    tts_f()
    

print('----end----')