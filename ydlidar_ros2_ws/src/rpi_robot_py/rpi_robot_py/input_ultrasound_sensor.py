import rclpy
from rclpy.node import Node
# from std_msgs.msg import Bool
from std_msgs.msg import Float32

# import pigpio
import time
import RPi.GPIO

# SENSOR_GPIO_PIN = 17 # 17番PINにセンサ接続
CENTER_IN = 26
CENTER_OUT = 15
TIMER_INTERVAL = 0.5

#障害物センサ測定関数
def Mesure(GPIO,time,trig,echo):
    dis = 0
    n = 1
    for i in range(n):
        sigoff = 0
        sigon = 0
        GPIO.output(trig,GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(trig,GPIO.LOW)
        kijyun=time.time()
        while(GPIO.input(echo)==GPIO.LOW):
            sigoff=time.time()
            if sigoff - kijyun > 0.02:
            #     print("break1")
                 break
        while(GPIO.input(echo)==GPIO.HIGH):
            sigon=time.time()
            if sigon - sigoff > 0.02:
            #     print("break2")
                 break
        d = (sigon - sigoff)*34000/2
        if d > 200:
            dis += 200/n
        else:
            dis += d/n
    return dis


class UltrasoundSensor(Node):
    def __init__(self):
        super().__init__('ultrasound_sensor_node')
        # self.init_sensor() # センサを使わない場合、不要
        self.init_GPIO()
        # self.pub_sensor = self.create_publisher(Bool, '/input/ultrasound_sensor', 10)
        self.pub_sensor = self.create_publisher(Float32, '/input/ultrasound_sensor', 10)
        self.timer = self.create_timer(TIMER_INTERVAL, self.sensor_timer_callback)
        self.prev_sensor_data = False

    def init_GPIO(self):
        self.GPIO = RPi.GPIO
        # GPIOピン番号の指示方法
        self.GPIO.setmode(self.GPIO.BOARD)

        #超音波センサ初期設定 中央
        self.GPIO.setup(CENTER_OUT, self.GPIO.OUT, initial=0)
        self.GPIO.setup(CENTER_IN, self.GPIO.IN)

    def sensor_timer_callback(self):
        # sensor_msg = Bool(data=self.get_sensor_data())
        sensor_msg = Float32(data=self.get_sensor_data())
        self.pub_sensor.publish(sensor_msg)


    # def init_sensor(self):
    #     self.pi = pigpio.pi()
    #     self.pi.set_mode(SENSOR_GPIO_PIN, pigpio.INPUT)
    #     self.pi.set_pull_up_down(SENSOR_GPIO_PIN, pigpio.PUD_UP)

    # センサを使わない場合、True/Falseを返す適当な関数に置きかえてください
    def get_sensor_data(self):
        # d = self.Measure_timeout(self, time, CENTER_OUT, CENTER_IN)
        d = Mesure(self.GPIO, time, CENTER_OUT, CENTER_IN)
        print('中央 -> {0:.1f}cm'.format(d))
        # return d < 20
        return d
        # if self.pi.read(SENSOR_GPIO_PIN) == 1:
        #     return True
        # else:
        #     return False


def main(args=None):
    rclpy.init(args=args)
    node = UltrasoundSensor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
