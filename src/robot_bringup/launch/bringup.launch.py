import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    bringup_dir = get_package_share_directory('robot_bringup')
    serial_bridge_dir = get_package_share_directory('serial_bridge')
    robot_description_dir = get_package_share_directory('robot_description')
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_slam',
            default_value='true',
            description='Launch SLAM Toolbox'
        ),
        DeclareLaunchArgument(
            'use_nav2',
            default_value='true',
            description='Launch Nav2'
        ),
        DeclareLaunchArgument(
            'map_file',
            default_value=os.path.join(bringup_dir, 'maps', 'map.yaml'),
            description='Path to map file for Nav2'
        ),
        
        # Robot state publisher
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(robot_description_dir, 'launch', 'robot_state_publisher.launch.py')
            ),
        ),
        
        # Serial bridge (motor control + odometry)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(serial_bridge_dir, 'launch', 'serial_bridge.launch.py')
            ),
        ),
        
        # SLAM Toolbox (if enabled)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(bringup_dir, 'launch', 'slam.launch.py')
            ),
            condition=None  # Add condition based on use_slam parameter if desired
        ),
        
        # Nav2 (if enabled)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(bringup_dir, 'launch', 'nav2.launch.py')
            ),
            condition=None  # Add condition based on use_nav2 parameter if desired
        ),
    ])
