import os
import sys

# 상위 디렉토리 추가 (for utils.config)
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg

# openpibo 라이브러리 경로 추가
sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from motion.motionlib import cMotion

import time

def move_test():
  m = cMotion(conf=cfg)

  for i in range (0,3):
  #while True:
    m.set_motors(positions=[0,0,20,-25,0,0,0,0,70,25], movetime=1000)
    time.sleep(1.1)
    m.set_motors(positions=[0,0,20, 0,0,0,0,0,70,25], movetime=1000)
    time.sleep(1.1)

if __name__ == "__main__":
  move_test()
