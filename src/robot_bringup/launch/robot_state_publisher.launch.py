import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command


def generate_launch_description():
    robot_description_dir = get_package_share_directory('robot_description')
    urdf_path = os.path.join(robot_description_dir, 'urdf', 'robot.urdf.xacro')
    
    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{
                'robot_description': Command(['xacro ', urdf_path]),
                'use_sim_time': False,
            }],
            output='screen'
        ),
    ])
