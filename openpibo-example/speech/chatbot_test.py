import os
import sys

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

def weather(cmd):
  lst, _type = ["오늘", "내일"], None

  for item in lst:
    if item in cmd:
      _type = item

  if _type == None:
    print("BOT > 오늘, 내일 날씨만 가능해요. ")
  else:
    print("BOT > {} 날씨 알려줄게요.".format(_type))


def music(cmd):
  lst, _type = ["발라드", "댄스", "락"], None

  for item in lst:
    if item in cmd:
      _type = item

  if _type == None:
    print("BOT > 발라드, 락, 댄스 음악만 가능해요.")
  else:
    print("BOT > {} 음악 틀어줄게요.".format(_type))

def news(cmd):
  lst, _type = ["경제", "스포츠", "문화"], None

  for item in lst:
    if item in cmd:
      _type = item

  if _type == None:
    print("BOT > 경제, 문화, 스포츠 뉴스만 가능해요.")
  else:
    print("BOT > {} 뉴스 알려줄게요.".format(_type))

db = {
  "날씨":weather,
  "음악":music, 
  "뉴스":news,
}

def main():
  obj = cDialog(conf=cfg)
  #speak = cSpeech(conf=cfg)
  print("대화 시작합니다.")
  while True:
    #print("입력 > ")
    c = input("입력 > ")
    #ret = speak.stt()
    #c = ret

    matched = False
    if c == "그만":
      break

    #print(obj)
    d = obj.mecab_morphs(c)
    print("\n형태소 분석: ", d)
    for key in db.keys():
      print(key, "---------") # 반복한다는 의미
      if key in d:
        db[key](d)
        #print(db[key](d))
        matched = True
    print()
    if matched == False:
      print("대화봇 > ", obj.get_dialog(c))

if __name__ == "__main__":
  main()
