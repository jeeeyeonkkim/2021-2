import sys
import time
import requests
import json
import os
import queue, os, threading
import soundfile as sf
import sounddevice as sd
from scipy.io.wavfile import write


# 상위 디렉토리 추가 (for utils.config)
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
#sys.path.append('/home/pi/openpibo-example/')
from utils.config import Config as cfg

# openpibo 라이브러리 경로 추가
sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from speech.speechlib import cDialog

# openpibo 라이브러리 경로 추가
sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from speech.speechlib import cSpeech

# openpibo 라이브러리 경로 추가
sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from speech.speechlib import cSpeech
from audio.audiolib import cAudio

# # 눈 색깔 
# sys.path.append(cfg.OPENPIBO_PATH + '/lib')
# from speech.speechlib import Edu_Pibo

kakao_speech_url = "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"
rest_api_key = '689f768b33cc755e92f496f3f0a245af'

headers = {
    "Content-Type": "application/octet-stream",
    "X-DSS-Service": "DICTATION",
    "Authorization": "KakaoAK " + rest_api_key,
}

def weather(cmd):
  lst, _type = ["오늘", "내일"], None

  for item in lst:
    if item in cmd:
      _type = item

  if _type == None:
    print("\tBOT > 오늘, 내일 날씨만 가능해요. ")
  else:
    print("\tBOT > {} 날씨 알려줄게요.".format(_type))


def music(cmd):
  lst, _type = ["발라드", "댄스", "락"], None

  for item in lst:
    if item in cmd:
      _type = item

  if _type == None:
    print("\tBOT > 발라드, 락, 댄스 음악만 가능해요.")
  else:
    print("\tBOT > {} 음악 틀어줄게요.".format(_type))

def news(cmd):
  lst, _type = ["경제", "스포츠", "문화"], None

  for item in lst:
    if item in cmd:
      _type = item

  if _type == None:
    print("\tBOT > 경제, 문화, 스포츠 뉴스만 가능해요.")
  else:
    print("\tBOT > {} 뉴스 알려줄게요.".format(_type))

db = {
  "날씨":weather,
  "음악":music, 
  "뉴스":news,
}

"""녹음 관련"""
def complicated_record():
    with sf.SoundFile("/home/pi/openpibo-example/speech/temp.wav", mode='w', samplerate=16000, subtype='PCM_16', channels=1) as file:
        with sd.InputStream(samplerate=16000, dtype='int16', channels=1, callback=complicated_save):
            while recording:
                file.write(q.get())

q = queue.Queue()
recorder = False
recording = False

def complicated_save(indata, frames, time, status):
	q.put(indata.copy())
    
def start():
    global recorder
    global recording
    recording = True
    recorder = threading.Thread(target=complicated_record)
    print('start recording')
    recorder.start()

def stop():
    global recorder
    global recording
    recording = False
    recorder.join()
    print('stop recording')

"""말하기 관련"""
def tts_f(message):
  tObj = cSpeech(conf=cfg)
  filename = cfg.TESTDATA_PATH+"/tts.mp3"
  tObj.tts("<speak>\
              <voice name='MAN_READ_CALM'>"+message+"<break time='500ms'/></voice>\
            </speak>"\
          , filename)
  print(filename)
  aObj = cAudio()
  aObj.play(filename, out='local', volume=-1500)

"""눈 색
def color_name_test():
    pibo = Edu_Pibo()
    ret=pibo.eye_on('purple', 'purple') # aqua
    print(ret)
    time.sleep(1)
    
    ret2=pibo.eye_on('pink')
    print(ret2)
    time.sleep(1)
    pibo.eye_off()
"""

def main():
  #speak = cSpeech(conf=cfg)
  obj = cDialog(conf=cfg)
  pib = Edu_Pibo()
  print(">>대화 시작합니다.")

  while True:
    recorder = False
    recording = False

    pib.eye_on('purple', 'purple') 
  
    start()

    time.sleep(7) #녹음되는 시간 6초 ..음성이 인식 될 때까지 녹음하는걸로 바꾸기
    ret=pibo.eye_on('aqua', 'aqua') 
    # print(ret)
    stop()

    with open('temp.wav', 'rb') as fp:
        audio = fp.read()

    res = requests.post(kakao_speech_url, headers=headers, data=audio)

    if "no result" in res.text: 
        print("말이 없으시군요..")
        continue

    result_json_string = res.text[res.text.index('{"type":"finalResult"'):res.text.rindex('}')+1]
    result = json.loads(result_json_string)
    
    #print(result['value'])
    speak = result['value'] # 음성->텍스트
    print("\t입력 > ", speak)

    matched = False
    if speak == "그만":
      break

    d = obj.mecab_morphs(speak)
    print("\n형태소 분석: ", d)
    for key in db.keys():
      print(key, "---------") # 반복한다는 의미
      if key in d:
        db[key](d)
        #print(db[key](d))
        matched = True
    print()
    if matched == False:
      print("\t대화봇 > ", obj.get_dialog(speak))
      tts_f(obj.get_dialog(speak))
      

if __name__ == "__main__":
  main()