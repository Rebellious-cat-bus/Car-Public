from glob import glob
from setuptools import setup

package_name = 'rpi_robot_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ## 後で作成する 'launch/*.launch.py'用に追記
        ('share/' + package_name, glob('launch/*.launch.py'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='neko',
    maintainer_email='syagi@student.42tokyo.jp',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    ## 追記
    entry_points={
        'console_scripts': [
            'ultrasound_sensor = rpi_robot_py.input_ultrasound_sensor:main',
            'servo = rpi_robot_py.output_servo:main',
            'controller = rpi_robot_py.controller:main',
            'controller_lazer = rpi_robot_py.controller_lazer:main',
        ],
    },
)
