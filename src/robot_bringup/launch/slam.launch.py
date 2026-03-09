import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    bringup_dir = get_package_share_directory('robot_bringup')
    slam_config = os.path.join(bringup_dir, 'config', 'slam_params.yaml')
    
    return LaunchDescription([
        Node(
            package='slam_toolbox',
            executable='sync_slam_toolbox_node',
            name='slam_toolbox',
            parameters=[slam_config],
            arguments=['--ros-args', '--log-level', 'info'],
            output='screen'
        ),
    ])
