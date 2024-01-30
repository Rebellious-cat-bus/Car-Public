import Adafruit_PCA9685
import time
pwm = Adafruit_PCA9685.PCA9685(address=0x40)
pwm.set_pwm_freq(60)

channel = 15
n=300
while(1):
    print(n)
    pwm.set_pwm(channel,0,n)
    time.sleep(1)
    n += 10
