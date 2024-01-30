#ros lib
import datetime
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

#commom lib
import math
import numpy as np
import time

# from yahboomcar_laser.common import *
print ("improt done")
RAD2DEG = 180 / math.pi

from std_msgs.msg import Float32
from std_msgs.msg import Int8

from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

ANGLE_MIN = -60
ANGLE_MAX = 60



# SIDE_ANGLE_MIN = -45
# SIDE_ANGLE_MAX = 45
# SIDE_WIDTH = 0.15

RAD2DEG = 180 / math.pi

class MyLazerController(Node):
    def __init__(self):
        super().__init__('controller_lazer_node')
        # self.pub_servo_left = self.create_publisher(Int8, '/output/servo/left', 10)
        # publiser
        self.pub_vel = self.create_publisher(Twist,'/cmd_vel',1)

        # qos_profile = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT,
            history=QoSHistoryPolicy.RMW_QOS_POLICY_HISTORY_KEEP_LAST,
            depth=1
        )
        # self.sub_laser = self.create_subscription(LaserScan,"/scan",self.registerScan, 1)
        self.sub_laser = self.create_subscription(LaserScan,"/scan",self.registerScan2, qos_profile)

        #declareparam
        self.declare_parameter("conv_num", 21)
        self.conv_num = int(self.get_parameter('conv_num').value)
        self.declare_parameter("speed_func", 0)
        self.speed_func = int(self.get_parameter('speed_func').value)
        self.declare_parameter("angle_func", 0)
        self.angle_func = int(self.get_parameter('angle_func').value)
        self.declare_parameter("sleep_msec", 0)
        self.sleep_msec = int(self.get_parameter('sleep_msec').value)
        self.get_logger().info('------------- params -----------')
        self.get_logger().info(f"conv_num:   {self.conv_num}")
        self.get_logger().info(f"speed_func: {self.speed_func}")
        self.get_logger().info(f"angle_func: {self.angle_func}")
        self.get_logger().info(f"sleep_msec: {self.sleep_msec}")
        self.get_logger().info('--------------------------------')
        self.Accelerate_mode_count = 0
        self.Accelerate_mode_rate = 1

    def logger_info(self, msg):
      t_delta = datetime.timedelta(hours=9)
      JST = datetime.timezone(t_delta, 'JST')
      now = datetime.datetime.now(JST)
      self.get_logger().info('{} {}'.format(now.strftime('%H:%M:%S'), msg))

    # (ANGLE_MIN, ANGLE_MAX)の間でconv_num個の平均が最も遠い点を探す
    def calc_max_angle_dist(self, scan_data, ranges):
        conv_idx_min = int(self.angle_to_conv_idx(ANGLE_MIN, scan_data.angle_min, scan_data.angle_increment))
        conv_idx_max = int(self.angle_to_conv_idx(ANGLE_MAX, scan_data.angle_min, scan_data.angle_increment))
        conv = np.convolve(ranges[conv_idx_min:conv_idx_max], np.ones(self.conv_num), mode='valid')
        # 最大値のインデックスを取得
        max_index = np.argmax(conv)

        # 最も遠い点の角度
        max_angle = (scan_data.angle_min + scan_data.angle_increment * (conv_idx_min + max_index + self.conv_num // 2 + 1)) * RAD2DEG
        # 平均距離
        max_distance = conv[max_index] / self.conv_num
        return (max_angle, max_distance)


    def angle_to_conv_idx(self, angle, angle_min, angle_increment) -> int:
        return (angle / RAD2DEG - angle_min) / angle_increment


    def registerScan2(self, scan_data):
        if not isinstance(scan_data, LaserScan): return
        ranges = np.array(scan_data.ranges)

        max_angle, max_distance = self.calc_max_angle_dist(scan_data, ranges)

        twist = Twist()
        speed = twist.linear.x = self.get_speed(max_distance)
        actual_angle = twist.angular.z = self.get_angle(scan_data, ranges, max_angle, max_distance)

        self.logger_info('{{max_angle: {:>7.2f}, actual_angle: {:>7.2f}, max_dist: {:>7.2f}, speed: {:>7.2f}}}'.format(max_angle, actual_angle, max_distance, speed))

        self.pub_vel.publish(twist)
        self.sleep()



    ########## 壁回避（うまく動かず） #########################################
    # 横（(-90 < x < -45), (45 <  < 90)）cos()が20cm以下の場合は回避する
    # def get_angle(self, scan_data, ranges, max_angle):
    #     conv_idx_min = int(self.angle_to_conv_idx(SIDE_ANGLE_MIN, scan_data.angle_min, scan_data.angle_increment))
    #     conv_idx_max = int(self.angle_to_conv_idx(SIDE_ANGLE_MAX, scan_data.angle_min, scan_data.angle_increment))

    #     abs_cos_r = np.abs(np.cos(ranges[:conv_idx_min]))
    #     abs_cos_l = np.abs(np.cos(ranges[:conv_idx_min]))

    #     idx_r = np.argmax(abs_cos_r)
    #     idx_l = np.argmax(abs_cos_l)

    #     if abs_cos_r[idx_r] < SIDE_WIDTH:
    #         self.get_logger().info("-------------avoid - 5")
    #         return max_angle - 5
    #     elif abs_cos_l[idx_l] < SIDE_WIDTH:
    #         self.get_logger().info("-------------avoid + 5")
    #         return max_angle + 5
    #     return max_angle

    #### sleep ################################################################################
    def sleep(self):
        if self.sleep_msec > 0:
            time.sleep(self.sleep_msec / 1000.0)

    #### angle ################################################################################
    def get_angle(self, scan_data, ranges, max_angle, max_distance):
        if self.angle_func == 0:
            return self.get_angle_0(scan_data, ranges, max_angle, max_distance)
        if self.angle_func == 1:
            return self.get_angle_1(scan_data, ranges, max_angle, max_distance)
        if self.angle_func == 2:
            return self.get_angle_2(scan_data, ranges, max_angle, max_distance)
        if self.angle_func == 3:
            return self.get_angle_3(scan_data, ranges, max_angle, max_distance)
        if self.angle_func == 4:
            return self.get_angle_4(scan_data, ranges, max_angle, max_distance)
        if self.angle_func == 5:
            return self.get_angle_5(scan_data, ranges, max_angle, max_distance)
        if self.angle_func == 6:
            return self.get_angle_6(scan_data, ranges, max_angle, max_distance)
        if self.angle_func == 7:
            return self.get_angle_7(scan_data, ranges, max_angle, max_distance)
        return 0.0

    def get_angle_0(self, scan_data, ranges, max_angle, max_distance):
        return max_angle

    def get_angle_1(self, scan_data, ranges, max_angle, max_distance):
        if max_distance > 0.5:
            return max_angle * 0.5
        return max_angle

    def get_angle_2(self, scan_data, ranges, max_angle, max_distance):
        if max_distance > 0.5:
            return max_angle * 0.3
        return max_angle

    def get_angle_3(self, scan_data, ranges, max_angle, max_distance):
        if max_distance > 0.5:
            return max_angle * 0.3
        return max_angle

    def get_angle_4(self, scan_data, ranges, max_angle, max_distance):
        if max_distance > 2.0:
            return max_angle * 0.3
        if max_distance > 0.5:
            return max_angle * 0.5
        return max_angle

    def get_angle_5(self, scan_data, ranges, max_angle, max_distance):
        if max_distance > 2.0:
            return max_angle * 0.3
        if max_distance > 1.0:
            return max_angle * 0.4
        if max_distance > 0.5:
            return max_angle * 0.5
        return max_angle

    def get_angle_6(self, scan_data, ranges, max_angle, max_distance):
        if max_distance > 0.5:
            return max_angle * 0.3
        return max_angle

    def get_angle_7(self, scan_data, ranges, max_angle, max_distance):
        if max_distance > 2.5:
            return max_angle * 0.1
        if max_distance > 2.0:
            return max_angle * 0.2
        if max_distance > 1.0:
            return max_angle * 0.3
        if max_distance > 0.5:
            return max_angle * 0.4
        return max_angle

    #### speed ################################################################################
    def get_speed(self, distance):
        if self.speed_func == 0:
            return self.get_speed_0(distance)
        if self.speed_func == 1:
            return self.get_speed_1(distance)
        if self.speed_func == 2:
            return self.get_speed_2(distance)
        if self.speed_func == 3:
            return self.get_speed_3(distance)
        if self.speed_func == 4:
            return self.get_speed_4(distance)
        if self.speed_func == 5:
            return self.get_speed_5(distance)
        if self.speed_func == 6:
            return self.get_speed_6(distance)
        if self.speed_func == 7:
            return self.get_speed_7(distance)
        if self.speed_func == 8:
            return self.get_speed_8(distance)
        if self.speed_func == 9:
            return self.get_speed_9(distance)
        if self.speed_func == 1000:
            return self.get_speed_1000(distance) # 10番
        if self.speed_func == 1001:
            return self.get_speed_1001(distance) # 10番のMaxを9.5に
        if self.speed_func == 1002:
            return self.get_speed_1002(distance) # 10番のMaxを9.0に
        if self.speed_func == 1003:
            return self.get_speed_1003(distance) # 10番のMaxを8.5に
        if self.speed_func == 11:
            return self.get_speed_11(distance)
        if self.speed_func == 1200:
            return self.get_speed_1200(distance) # 10番のたまに減速するやつ
        if self.speed_func == 1201:
            return self.get_speed_1201(distance) # 1200より若干はええやつ
        if self.speed_func == 1202:
            return self.get_speed_1202(distance) # 1200より若干遅いやつ
        if self.speed_func == 1203:
            return self.get_speed_1203(distance) # 1200より滑って遅くしました。
        self.logger_info('speed_func is invalid')
        return 0.0

    def get_speed_0(self, distance):
        if distance < 0.3:
            return 0.0
        if distance < 1.0:
            return 2.0
        if distance < 2.0:
            return 3.0
        return 4.0

    def get_speed_1(self, distance):
        if distance < 8.0:
            return distance * 1.0
        return 8.0

    def get_speed_2(self, distance):
        if distance < 0.3:
            return 0.0
        if distance < 0.5:
            return 1.0
        if distance < 1.0:
            return 3.0
        if distance < 2.0:
            return 5.0
        if distance < 3.0:
            return 6.0
        return 10.0

    def get_speed_3(self, distance):
        if distance < 0.3:
            return 0.0
        if distance < 1.0:
            return 2.0
        if distance < 2.0:
            return 4.0
        return 6.0

    def get_speed_4(self, distance):
        if distance < 0.3:
            return 0.0
        if distance < 1.0:
            return 2.0
        if distance < 2.5:
            return 4.5
        return 7.0

    def get_speed_5(self, distance): # ここ変える
        if distance < 0.3:
            return 0.0
        if distance < 1.0:
            return 3.0
        if distance < 2.5:
            return 4.5
        if distance < 4:
            return 7.5
        return 10.0

    def get_speed_6(self, distance): # ここ変える
        if distance < 0.3:
            return 0.0
        if distance < 1.0:
            return 3.0
        if distance < 2.0: # 曲がりきれなかったら 2.5 -> 3
            return 5.0
        if distance < 3:
            return 7.5
        # if distance < 4:
        #     return 8.5
        return 10.0

    def get_speed_7(self, distance): # 結構自信ありby tsishika
        if distance < 1.0:
            return 3.0
        if distance < 2.0: # 曲がりきれなかったら 2.5 -> 3
            return 5.0
        if distance < 2.3:
            return 5.5
        if distance < 2.6:
            return 6.5
        if distance < 3:
            return 7.5
        if distance < 3.3:
            return 8.5
        return 10.0

    def get_speed_8(self, distance): # 減速モード搭載
        if self.Accelerate_mode_count > 10:
            self.Accelerate_mode_count = 0
            self.Accelerate_mode_rate = 1
        if distance < 1.0:
            return 3.0 * self.Accelerate_mode_rate
        if distance < 2.0:
            return 5.0 * self.Accelerate_mode_rate
        if distance < 2.3:
            return 5.5 * self.Accelerate_mode_rate
        if distance < 2.6:
            return 6.5 * self.Accelerate_mode_rate
        if distance < 3:
            return 7.5 * self.Accelerate_mode_rate
        if distance < 3.3:
            return 8.5 * self.Accelerate_mode_rate
        self.Accelerate_mode_count += 1
        self.Accelerate_mode_rate = 0.7
        return 10.0

    def get_speed_9(self, distance): # 安全に行きたい
        if distance < 2.0:
            return 3.0
        if distance < 2.3:
            return 4.5
        if distance < 2.6:
            return 5.5
        if distance < 3:
            return 6.5
        if distance < 3.3:
            return 7.0
        if distance < 3.6:
            return 7.5
        return 8.5

    def get_speed_1000(self, distance):
        if distance < 2.0:
            return 3.0
        if distance < 2.3:
            return 4.5
        if distance < 2.6:
            return 5.5
        if distance < 3:
            return 6.5
        if distance < 3.3:
            return 7.0
        if distance < 3.6:
            return 7.5
        return 10.0

    def get_speed_1001(self, distance):
        if distance < 2.0:
            return 3.0
        if distance < 2.3:
            return 4.5
        if distance < 2.6:
            return 5.5
        if distance < 3:
            return 6.5
        if distance < 3.3:
            return 7.0
        if distance < 3.6:
            return 7.5
        return 9.5

    def get_speed_1002(self, distance):
        if distance < 2.0:
            return 3.0
        if distance < 2.3:
            return 4.5
        if distance < 2.6:
            return 5.5
        if distance < 3:
            return 6.5
        if distance < 3.3:
            return 7.0
        if distance < 3.6:
            return 7.5
        return 9.0

    def get_speed_1003(self, distance):
        if distance < 2.0:
            return 3.0
        if distance < 2.3:
            return 4.5
        if distance < 2.6:
            return 5.5
        if distance < 3:
            return 6.5
        if distance < 3.3:
            return 7.0
        if distance < 3.6:
            return 7.5
        return 8.5

    def get_speed_11(self, distance): # 減速モード搭載
        if self.Accelerate_mode_count > 10:
            if distance < 3.3:
                self.Accelerate_mode_count = 0
                self.Accelerate_mode_rate = 0.7
        if distance < 1.0:
            return 3.0 * self.Accelerate_mode_rate
        if distance < 2.0:
            return 5.0 * self.Accelerate_mode_rate
        if distance < 2.3:
            return 5.5 * self.Accelerate_mode_rate
        if distance < 2.6:
            return 6.5 * self.Accelerate_mode_rate
        if distance < 3:
            return 7.5 * self.Accelerate_mode_rate
        if distance < 3.3:
            return 8.5 * self.Accelerate_mode_rate
        self.Accelerate_mode_count += 1
        self.Accelerate_mode_rate = 1
        return 10.0

    def get_speed_1200(self, distance):
        if distance < 2.0:
            return 3.0
        if distance < 2.3:
            return 4.5
        if distance < 2.6:
            return 5.5
        if distance < 3:
            return 6.5
        if distance < 3.3:
            return 7.0
        if distance < 3.6:
            return 7.5
        self.Accelerate_mode_count += 1
        self.Accelerate_mode_rate = 1
        if self.Accelerate_mode_count > 10:
            self.Accelerate_mode_count = 0
            self.Accelerate_mode_rate = 0.8
        return 10.0 * self.Accelerate_mode_rate

    def get_speed_1201(self, distance):
        if distance < 2.0:
            return 3.0
        if distance < 2.3:
            return 4.5
        if distance < 2.6:
            return 5.5
        if distance < 3:
            return 6.5
        if distance < 3.3:
            return 7.0
        if distance < 3.6:
            return 7.5
        self.Accelerate_mode_count += 1
        self.Accelerate_mode_rate = 1
        if self.Accelerate_mode_count > 10:
            self.Accelerate_mode_count = 0
            self.Accelerate_mode_rate = 0.9
        return 10.0 * self.Accelerate_mode_rate

    def get_speed_1202(self, distance):
        if distance < 2.0:
            return 3.0
        if distance < 2.3:
            return 4.5
        if distance < 2.6:
            return 5.5
        if distance < 3:
            return 6.5
        if distance < 3.3:
            return 7.0
        if distance < 3.6:
            return 7.5
        self.Accelerate_mode_count += 1
        self.Accelerate_mode_rate = 1
        if self.Accelerate_mode_count > 10:
            self.Accelerate_mode_count = 0
            self.Accelerate_mode_rate = 0.7
        return 10.0 * self.Accelerate_mode_rate

    def get_speed_1203(self, distance):
        if distance < 2.0:
            return 3.0
        if distance < 2.3:
            return 4.0
        if distance < 2.6:
            return 5.0
        if distance < 3:
            return 6.0
        if distance < 3.3:
            return 6.5
        if distance < 3.6:
            return 7.0
        self.Accelerate_mode_count += 1
        self.Accelerate_mode_rate = 1
        if self.Accelerate_mode_count > 7:
            self.Accelerate_mode_count = 0
            self.Accelerate_mode_rate = 0.7
        return 10.0 * self.Accelerate_mode_rate


def main(args=None):
    # with open('config.yml', 'r') as yml:
    # config = yaml.load(yml)

    # print('--- A ---')
    # print('name: ', config['hyperparameterA']['name'])
    # print('--------------------------')
    # print(sys.argv)
    # print('--------------------------')

    rclpy.init(args=args)
    node = MyLazerController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
