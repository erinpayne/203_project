# Wheeled Autonomous Robot - SLAM & Navigation

A ROS2-based autonomous navigation stack for a differential drive wheeled robot using SLAM Toolbox, RPLidar, and Nav2.

## Project Overview

This project implements a complete autonomy stack with:
- **Hardware**: Differential drive robot with wheel encoders and RPLidar
- **Motor Control**: Arduino-based motor driver via serial bridge
- **SLAM**: SLAM Toolbox for real-time mapping and localization
- **Navigation**: Nav2 for autonomous path planning and obstacle avoidance
- **Middleware**: ROS2 for sensor integration and system control

## Project Structure

```
203_project/
├── src/
│   ├── robot_description/          # Robot URDF and kinematics
│   ├── serial_bridge/              # Arduino serial communication
│   ├── robot_bringup/              # Launch files and configurations
│   │   ├── launch/                 # bringup.launch.py, slam.launch.py, nav2.launch.py
│   │   ├── config/                 # SLAM and Nav2 YAML parameters
│   │   └── maps/                   # Saved maps (map.yaml)
│   └── ...
├── firmware/
│   └── arduino_motor_controller/   # Arduino firmware (.ino)
└── README.md
```

## Hardware Requirements

- **Robot Platform**: Differential drive with two DC motors
- **Encoders**: Wheel encoders (600 CPR recommended)
- **Lidar**: Slamtec RPLidar
- **Microcontroller**: Arduino Uno/Mega for motor control
- **Computer**: SBC (Raspberry Pi, Jetson Nano) or laptop running ROS2

## Software Stack

- **ROS2**: Latest LTS distribution (Humble recommended)
- **SLAM Toolbox**: Real-time visual SLAM
- **Nav2**: Navigation framework
- **RPLidar ROS2 Driver**: Lidar scanning

## Quick Start

### 1. Build ROS2 Packages

```bash
cd ~/203_project
colcon build
source install/setup.bash
```

### 2. Configure Hardware

Edit hardware parameters in `src/serial_bridge/launch/serial_bridge.launch.py`:
- Serial port (`/dev/ttyUSB0` or `/dev/ttyACM0` on Linux, `COM3` on Windows)
- Encoder CPR (counts per revolution)
- Wheel radius and separation

Edit RPLidar port and parameters in bringup launch file.

### 3. Upload Arduino Firmware

1. Open `firmware/arduino_motor_controller/arduino_motor_controller.ino` in Arduino IDE
2. Adjust pin configuration for your hardware
3. Upload to Arduino board

### 4. Launch Robot Autonomy Stack

```bash
ros2 launch robot_bringup bringup.launch.py
```

This launches:
- Robot state publisher (URDF)
- Serial bridge (motor control + odometry)
- SLAM Toolbox (mapping and localization)
- Nav2 stack (path planning and navigation)

## Configuration Files

### Robot Description
- `src/robot_description/urdf/robot.urdf.xacro` — Robot kinematic model
- `src/robot_description/urdf/properties.yaml` — Robot dimensions and mass

### Serial Bridge
- `src/serial_bridge/serial_bridge_node.py` — ROS2 node for Arduino communication

### SLAM Parameters
- `src/robot_bringup/config/slam_params.yaml` — SLAM Toolbox tuning for RPLidar

### Nav2 Parameters
- `src/robot_bringup/config/nav2_params.yaml` — Navigation stack configuration
- `src/robot_bringup/config/local_costmap_params.yaml` — Local obstacle costmap
- `src/robot_bringup/config/global_costmap_params.yaml` — Global static costmap
- `src/robot_bringup/config/planner_params.yaml` — Path planner configuration

## Operating Modes

### Mapping Mode
```bash
ros2 launch robot_bringup bringup.launch.py use_slam:=true use_nav2:=false
```
Drives the robot around your environment to build a map. Save the map:
```bash
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap "{name: {data: '/path/to/maps/my_map'}}"
```

### Navigation Mode
```bash
ros2 launch robot_bringup bringup.launch.py use_slam:=false use_nav2:=true map_file:=/path/to/maps/my_map.yaml
```
Uses pre-built map for autonomous navigation.

### SLAM + Navigation
```bash
ros2 launch robot_bringup bringup.launch.py use_slam:=true use_nav2:=true
```
Simultaneously maps and navigates (requires more processing power).

## Troubleshooting

### Serial Connection Issues
- Verify Arduino is detected: `ls /dev/tty*`
- Check serial bridge node parameters (port, baudrate)
- Ensure Arduino has motor control firmware loaded

### SLAM Not Converging
- Check lidar scan topic: `ros2 topic echo /scan`
- Verify frame transforms: `ros2 run tf2_tools view_frames`
- Adjust SLAM parameters in `slam_params.yaml`

### Nav2 Navigation Failing
- Ensure SLAM is providing good odometry
- Check costmap inflation radius and obstacle detection
- Verify map is loaded correctly

## Next Steps

1. **Calibrate Odometry** — Drive straight and verify encoder reading accuracy
2. **Tune SLAM Parameters** — Adjust scan matcher sensitivity for your environment
3. **Optimize Navigation** — Tune costmap inflation and planner parameters for your robot
4. **Test Autonomous Missions** — Create navigation goals and validate path planning

## References

- [ROS2 Documentation](https://docs.ros.org/)
- [SLAM Toolbox](https://github.com/SteveMacenski/slam_toolbox)
- [Nav2 Documentation](https://docs.nav2.org/)
- [RPLidar ROS2 Driver](https://github.com/allenh1/rplidar_ros)