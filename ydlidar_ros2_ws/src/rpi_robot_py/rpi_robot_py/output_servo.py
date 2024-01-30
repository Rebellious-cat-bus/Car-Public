import datetime
import rclpy
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor
# from rclpy.executors import MultiThreadedExecutor

from geometry_msgs.msg import Twist

import Adafruit_PCA9685

import random

# Steering
SERVO_MAX = 450
SERVO_MIN = 250

ANGLE_MIN = -30
ANGLE_MAX = 30

# Accel
ACCEL_FRONT = 310
ACCEL_STOP = 360
ACCEL_BACK = 410

SPEED_MAX = 10
SPEED_MIN = -10

# PCA9685 の 0 と 3 に、2つのサーボを接続
SERVO_ANGLE_ID = 14
SERVO_ACCELL_ID = 15

class Servo(Node):
    def __init__(self):
        super().__init__('drive_node')
        self.init_pca9685() # サーボを使わない場合、不要
        self.sub_servo = self.create_subscription(Twist, '/cmd_vel', self.servo_callback, 10)


    def init_pca9685(self):
        self.pwm = Adafruit_PCA9685.PCA9685(address=0x40)
        self.pwm.set_pwm_freq(60)

    def servo_callback(self, servo_msg):
      linear_speed = servo_msg.linear.x  # 線形速度
      angular_speed = servo_msg.angular.z  # 角速度
      self.set_angle(angular_speed)
      self.set_accel(linear_speed)

    def set_angle(self, angular_speed):
      pulse = self.angle_to_pulse(angular_speed)
      self.pwm.set_pwm(SERVO_ANGLE_ID, 0, int(pulse))

    def set_accel(self, linear_speed):
      pulse = self.speed_to_pulse(linear_speed)
      self.pwm.set_pwm(SERVO_ACCELL_ID, 0, int(pulse))

    def angle_to_pulse(self, angle):
      pulse = (SERVO_MAX - SERVO_MIN) / (ANGLE_MAX * 2) * (-angle + ANGLE_MAX) + SERVO_MIN
      return pulse

    def speed_to_pulse(self, speed):
      accel = (ACCEL_BACK - ACCEL_FRONT) / (SPEED_MAX * 2) * (-speed + SPEED_MAX) + ACCEL_FRONT
      return accel

def main(args=None):
    rclpy.init(args=args)

    executor = SingleThreadedExecutor()
    ## mutli thread の場合はこっち
    # executor = MultiThreadedExecutor(num_threads=2)

    ## ノード（クラス）を2つインスタンス化し、executor に登録
    node = Servo()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        node.set_angle(0)
        node.set_accel(0)
        pass

    executor.shutdown()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
