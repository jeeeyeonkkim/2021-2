#!/usr/bin/python
import socket
import cv2
import numpy
import os
import sys
import time
import ast
import json

# 상위 디렉토리 추가 (for utils.config)
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg

# openpibo 라이브러리 경로 추가
sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from vision.visionlib import cCamera

# openpibo 라이브러리 경로 추가
sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from motion.motionlib import cMotion

#연결할 서버(수신단)의 ip주소와 port번호
TCP_IP = '192.168.0.76'
TCP_PORT = 1234
#송신을 위한 socket 준비
sock = socket.socket()

sock.connect((TCP_IP,TCP_PORT))
#OpenCV를 이용해서 webcam으로 부터 이미지 추출
cam = cCamera()
capture = cv2.VideoCapture(0)
m = cMotion(conf=cfg)
m.set_motors(positions=[0,0,-70,-25,0,0,0,0,70,25], movetime=5000)
time.sleep(3)
motion_list = []
while True :
    #frame = cam.read()
    ret, frame = capture.read()
    #cam.imwrite("test.jpg", frame)
    frame = cv2.flip(frame,1)

    #추출한 이미지를 String 형태로 변환(인코딩)시키는 과정
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
    result, imgencode = cv2.imencode('.jpg', frame, encode_param)
    data = numpy.array(imgencode)
    stringData = data.tobytes()
    #stringData = data.tostring()

    #String 형태로 변환한 이미지를 socket을 통해서 전송
    sock.send( str(len(stringData)).ljust(16).encode())
    sock.send( stringData )

    #파이보로부터 motion data 수신했는지 판단 여부
    motion_send = sock.recv(1024).decode('utf-8')

    if motion_send == '1' :
        # 파이보로부터 Motion data 수신
        motion_list = sock.recv(1024)
        motion_list = eval(motion_list)
        motionData_x = int(motion_list[0])
        motionData_y = int(motion_list[1])
        motion_list = []
        m.set_motors(positions=[0,0,-70,-25,motionData_x,motionData_y,0,0,70,25], movetime=30000)

cv2.destroyAllWindows() 
sock.close()