# Car

## 仕様技術
- raspberry pi 4 (ubuntu 22.04)
- LiDAR

## How to use

```bash
git clone git@github.com:Rebellious-cat-bus/Car-Public.git
cd ydlidar_ros2_ws/src
git clone git@github.com:Rebellious-cat-bus/ydlidar_ros2_driver.git
cd ..
colcon build
ros2 launch rpi_robot_py rpi_robot_lazer1003_0.launch.py
```

ビルドが完了しているなら、リビルドせずに以下のコマンドで起動できます。
```bash
rpi_robot_lazer1003_0.launch.py {./ydlidar_ros2_ws/src/rpi_robot_py/launch内にあるpythonファイル名}
```
___
### ROS2のインストール
ROS公式
https://www.ros.org/blog/getting-started/
(公式ではUbuntuを推奨)

RaspberryPi OSではじめるROS2
https://zenn.dev/array/books/5efdb438cf8be3

ラズパイOS + ROS2
https://github.com/Ar-Ray-code/rpi-bullseye-ros2

仕様バージョン
ubuntu 22.04 + ROS2(humble)

ROSの起動テスト
```
source /opt/ros/humble/setup.bash
ros2 run demo_nodes_cpp talker
```

https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Configuring-ROS2-Environment.html

```
# 起動スクリプトにROSのsourceを追加
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

# ドメインID設定
echo "export ROS_DOMAIN_ID=0" >> ~/.bashrc
```

https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Colcon-Tutorial.html

colcon
```
sudo apt install python3-colcon-common-extensions
```
___
### LiDARの起動、インストール
公式ドキュメント
https://github.com/YahboomTechnology/EAI-X3-X3ProLidar/tree/main

公式リポジトリ
https://github.com/YDLIDAR/ydlidar_ros2

RPi4 ROS YDLIDAR X4でSLAM(しらん人のブログ)（ROS1）
https://www.hirotakaster.com/weblog/rpi4-ros-ydlidar-x4%E3%81%A7slam/

ROS2 YDLIDAR
https://qiita.com/Yuya-Shimizu/items/c516b076ecc15864c0c5

とりあえず、テストは動くようになった。

参考
https://qiita.com/Yuya-Shimizu/items/c516b076ecc15864c0c5

SDKリポジトリ
https://github.com/YDLIDAR/YDLidar-SDK

doc/howto/how_to_build_and_install.md　
に従ってインストール

```
sudo apt-get install swig python3-pip
```

権限付与
```
sudo chmod 777 /dev/ttyUSB0
```

動作確認
```
tri_test
```
___
### ydlidar_ros2_driverのインストール
公式ではコンパイルエラー

このプルリクを使ったら動いた
https://github.com/YDLIDAR/ydlidar_ros2_driver/pull/20/files

プルリク元のリポジトリ
https://github.com/lghrainbow/ydlidar_ros2_driver/tree/humble-devel

ydlidar.yamlは下記サイトのydlidar_ros2_driver-master.tar.xzからコピー
https://drive.google.com/drive/folders/1vhsOBAJUoUXyGVaeOHBRd-IeaozHdOJS


READMEに沿ってビルド

テスト
```
ros2 launch ydlidar_ros2_driver ydlidar_launch_view.py 
```
