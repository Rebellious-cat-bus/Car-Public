from launch import LaunchDescription
from launch_ros.actions import Node

import os
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    share_dir = get_package_share_directory('ydlidar_ros2_driver')
    rviz_config_file = os.path.join(share_dir, 'config','ydlidar.rviz')

    lidar_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
         get_package_share_directory('ydlidar_ros2_driver'), 'launch'),
         '/ydlidar_launch.py'])
      )
    rviz2_node = Node(package='rviz2',
                    executable='rviz2',
                    name='rviz2',
                    arguments=['-d', rviz_config_file],
                    )

    return LaunchDescription([
        lidar_node,
        Node(
            package='rpi_robot_py',
            executable='servo',
            # output='screen'
        ),
        Node(
            package='rpi_robot_py',
            executable='controller_lazer',
            output='screen',
            emulate_tty=True,
            parameters=[os.path.join(os.getcwd(), 'src/rpi_robot_py/params/', 'controller_001_0.yaml')]
        ),
        rviz2_node,
    ])
