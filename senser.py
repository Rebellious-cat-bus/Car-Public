import time
import RPi.GPIO as GPIO

#障害物センサ測定関数
def Measure(GPIO,time,trig,echo):
    sigon = 0 #Echoピンの電圧が0V→3.3Vに変わった時間を記録する変数
    sigoff = 0 #Echoピンの電圧が3.3V→0Vに変わった時間を記録する変数
    GPIO.output(trig,1) #Trigピンの電圧をHIGH(3.3V)にする
    time.sleep(0.00001) #10μs待つ
    GPIO.output(trig,0) #Trigピンの電圧をLOW(0V)にする
    while(GPIO.input(echo)==0):
        sigon=time.time() #Echoピンの電圧がHIGH(3.3V)になるまで、sigonを更新
    while(GPIO.input(echo)==1):
        sigoff=time.time() #Echoピンの電圧がLOW(0V)になるまで、sigoffを更新
    d = (sigoff - sigon)*34000/2 #距離を計算(単位はcm)
    if d > 200:
        d = 200 #距離が200cm以上の場合は200cmを返す
    return d

# GPIOピン番号の指示方法
GPIO.setmode(GPIO.BOARD)

#超音波センサ初期設定 中央
# Trig -- 15
GPIO.setup(15 ,GPIO.OUT,initial=0)
# Echo -- 26
GPIO.setup(26 ,GPIO.IN)

#超音波センサ初期設定 左
# Trig -- 13
GPIO.setup(13 ,GPIO.OUT,initial=0)
# Echo -- 24
GPIO.setup(24 ,GPIO.IN)

#超音波センサ初期設定 右
# Trig -- 32
GPIO.setup(32, GPIO.OUT,initial=0)
# Echo -- 31
GPIO.setup(31, GPIO.IN)

try:
    while True:
        #Frセンサ距離
        print('------------------')
        d = Measure(GPIO,time,15, 26)
        print('中央 -> {0:.1f}cm'.format(d))
        d = Measure(GPIO,time,13, 24)
        print('左   -> {0:.1f}cm'.format(d))
        d = Measure(GPIO,time,32, 31)
        print('右   -> {0:.1f}cm'.format(d))
        time.sleep(1)

except KeyboardInterrupt:
    print('stop!')
    GPIO.cleanup()
