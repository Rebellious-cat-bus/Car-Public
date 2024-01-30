import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from std_msgs.msg import Int8

import random

# ANGLE_MIN = -70
# ANGLE_MAX = 70
ANGLE_MIN = -45
ANGLE_MAX = 45

class MyController(Node):
    def __init__(self):
        super().__init__('controller_node')
        # self.prev_sensor_data = False
        self.pub_servo_left = self.create_publisher(Int8, '/output/servo/left', 10)
        # self.pub_servo_right = self.create_publisher(Int8, '/output/servo/right', 10)
        # self.sub_sensor = self.create_subscription(Bool, '/input/human_sensor', self.sensor_callback, 10)
        self.sub_sensor = self.create_subscription(Float32, '/input/ultrasound_sensor', self.sensor_callback, 10)


    def sensor_callback(self, sensor_msg):
        angle = int(sensor_msg.data * 2.0 - 45.0)
        if angle > 45:
            angle =  45
        elif angle < -45:
            angle = -45
        self.pub_servo_left.publish( Int8(data=angle) )
        # if self.prev_sensor_data != sensor_msg.data:
        #     self.prev_sensor_data = sensor_msg.data
        #     if sensor_msg.data == True:
        #         self.pub_servo_left.publish( Int8(data=random.randint(ANGLE_MIN, ANGLE_MAX)) )
        #     else: 
        #         self.pub_servo_left.publish( Int8(data=random.randint(ANGLE_MIN, ANGLE_MAX)) )
        #         # self.pub_servo_right.publish( Int8(data=random.randint(ANGLE_MIN, ANGLE_MAX)) )


def main(args=None):
    rclpy.init(args=args)
    node = MyController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
