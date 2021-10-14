import queue, os, threading
import sounddevice as sd
import soundfile as sf
from scipy.io.wavfile import write
import time
import requests
import json

kakao_speech_url = "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"
rest_api_key = '689f768b33cc755e92f496f3f0a245af'

headers = {
    "Content-Type": "application/octet-stream",
    "X-DSS-Service": "DICTATION",
    "Authorization": "KakaoAK " + rest_api_key,
}

q = queue.Queue()
recorder = False
recording = False

def complicated_record():
    with sf.SoundFile("/home/pi/openpibo-example/speech/temp.wav", mode='w', samplerate=16000, subtype='PCM_16', channels=1) as file:
        with sd.InputStream(samplerate=16000, dtype='int16', channels=1, callback=complicated_save):
            while recording:
                file.write(q.get())
        
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
    print('stop recording' )
    
start()
time.sleep(6)
stop()

with open('temp.wav', 'rb') as fp:
    audio = fp.read()

res = requests.post(kakao_speech_url, headers=headers, data=audio)
print(res)
print()
print("res.text:", res.text)
result_json_string = res.text[res.text.index('{"type":"finalResult"'):res.text.rindex('}')+1]
print("result_json_string:",result_json_string)
result = json.loads(result_json_string)
#print(result)
print("value:",result['value'])