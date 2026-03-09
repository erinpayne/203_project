import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'port',
            default_value='/dev/ttyUSB0',
            description='Serial port for Arduino'
        ),
        DeclareLaunchArgument(
            'baudrate',
            default_value='115200',
            description='Serial baud rate'
        ),
        Node(
            package='serial_bridge',
            executable='serial_bridge_node',
            name='serial_bridge',
            parameters=[
                {'port': LaunchConfiguration('port')},
                {'baudrate': LaunchConfiguration('baudrate')},
                {'wheel_radius': 0.05},
                {'wheel_separation': 0.2},
                {'encoder_cpr': 600},
            ],
            output='screen'
        ),
    ])
