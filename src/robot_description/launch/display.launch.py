import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    robot_description_path = get_package_share_directory('robot_description')
    urdf_path = os.path.join(robot_description_path, 'urdf', 'robot.urdf.xacro')
    rviz_config_path = os.path.join(robot_description_path, 'rviz', 'robot.rviz')

    robot_description_content = ParameterValue(
        Command(['xacro ', urdf_path]),
        value_type=str
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'
        ),
        # Robot State Publisher - broadcasts robot TF
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[
                {'robot_description': robot_description_content},
                {'use_sim_time': LaunchConfiguration('use_sim_time')},
            ],
            output='screen'
        ),
        # RViz2 for visualization
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_path],
            output='screen'
        ),
    ])

