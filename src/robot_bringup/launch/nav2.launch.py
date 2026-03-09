import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument


def generate_launch_description():
    bringup_dir = get_package_share_directory('robot_bringup')
    nav2_config = os.path.join(bringup_dir, 'config', 'nav2_params.yaml')
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'map_file',
            default_value=os.path.join(bringup_dir, 'maps', 'map.yaml'),
            description='Path to nav2 map'
        ),
        
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            parameters=[
                {'yaml_filename': LaunchConfiguration('map_file')}
            ],
            output='screen'
        ),
        
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            parameters=[nav2_config],
            output='screen'
        ),
        
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            parameters=[nav2_config],
            output='screen'
        ),
        
        Node(
            package='nav2_behavior_server',
            executable='behavior_server',
            name='behavior_server',
            parameters=[nav2_config],
            output='screen'
        ),
        
        Node(
            package='nav2_costmap_2d',
            executable='costmap_filter_info_server',
            name='costmap_filter_info_server',
            parameters=[nav2_config],
            output='screen'
        ),
    ])
