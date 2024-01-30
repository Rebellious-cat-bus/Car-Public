import Adafruit_PCA9685
import time
import RPi.GPIO as GPIO
  
pwm_accel = Adafruit_PCA9685.PCA9685(address=0x40)
pwm_handle = Adafruit_PCA9685.PCA9685()
handle_channel = 0
accel_channel = 1

# Set frequency to 60hz, good for servos.
pwm_handle.set_pwm_freq(60)
pwm_accel.set_pwm_freq(60)

# Argument
run_speed = 345
low_speed = 350
stop_speed = 400
servo_min = 290  # Min pulse length out of 4096
servo_max = 490  # Max pulse length out of 4096
servo_mid = 390  # Max pulse length out of 4096


#障害物センサ測定関数
def Measure(GPIO, time, trig, echo):
    sigon = 0 #Echoピンの電圧が0V→3.3Vに変わった時間を記録する変数
    sigoff = 0 #Echoピンの電圧が3.3V→0Vに変わった時間を記録する変数
    GPIO.output(trig, 1) #Trigピンの電圧をHIGH(3.3V)にする
    time.sleep(0.00001) #10μs待つ
    GPIO.output(trig, 0) #Trigピンの電圧をLOW(0V)にする
    time.sleep(0.00001) #10μs待つ
    while(GPIO.input(echo) == 0):
        sigon=time.time() #Echoピンの電圧がHIGH(3.3V)になるまで、sigonを更新
    while(GPIO.input(echo) == 1):
        sigoff=time.time() #Echoピンの電圧がLOW(0V)になるまで、sigoffを更新
    d = (sigoff - sigon) * 34000 / 2 #距離を計算(単位はcm)
    if d > 200:
        d = 200 #距離が200cm以上の場合は200cmを返す
    return d

def Measure_loop(GPIO, time, trig, echo):
    d = 0
    loop_counter = 0
    for i in range(20):
        tmp = Measure(GPIO, time, trig, echo)
        if tmp != 200:
            d += Measure(GPIO, time, trig, echo)
            loop_counter += 1
    if loop_counter == 0:
        return 200
    return d / loop_counter

#障害物センサ測定関数(タイムアウト付き)
def Measure_timeout(GPIO, time, trig, echo, max_attempts=10, timeout=0.02):
    attempts = 0

    while attempts < max_attempts:
        try:
            result = Measure(GPIO, time, trig, echo)
            return result
        except:
            print("Measurement failed. Retrying...")
            attempts += 1
            time.sleep(timeout)
    print(f"Measurement timed out after {max_attempts} attempts.")
    return 200  # または、エラーを示す特定の値を返す


def init_GPIO():
    # GPIOピン番号の指示方法
    GPIO.setmode(GPIO.BOARD)

	#超音波センサ初期設定 中央
    GPIO.setup(15, GPIO.OUT, initial=0)
    GPIO.setup(26, GPIO.IN)

	#超音波センサ初期設定 左
    GPIO.setup(13, GPIO.OUT, initial=0)
    GPIO.setup(24, GPIO.IN)

	#超音波センサ初期設定 右
    GPIO.setup(32 ,GPIO.OUT, initial=0)
    GPIO.setup(31 ,GPIO.IN)

init_GPIO()
try:
    while True:
        #Frセンサ距離
        print('------------------')
        d = Measure_timeout(GPIO,time, 15, 26)
        print('中央 -> {0:.1f}cm'.format(d))
        # if (d < 40):
        #     pwm_accel.set_pwm(accel_channel, 0, low_speed)
        # else:
        pwm_accel.set_pwm(accel_channel, 0, run_speed)
        left_length = Measure_timeout(GPIO,time, 13, 24)
        right_length = Measure_timeout(GPIO,time, 32, 31)
        print('左   -> {0:.1f}cm'.format(left_length))
        print('右   -> {0:.1f}cm'.format(right_length))
        if (left_length < right_length):
            pwm_handle.set_pwm(handle_channel, 0, servo_max)
            print('go right!')
        else:
            pwm_handle.set_pwm(handle_channel, 0, servo_min)
            print('go left!')
        time.sleep(0.5)
  
except KeyboardInterrupt:
    print('stop!')
    pwm_accel.set_pwm(accel_channel, 0, 400)
    GPIO.cleanup()