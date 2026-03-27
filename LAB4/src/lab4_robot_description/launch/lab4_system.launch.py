import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node

def generate_launch_description():
    
    pkg_name = 'lab4_robot_description'
    pkg_share = get_package_share_directory(pkg_name)

    urdf_file = os.path.join(pkg_share, 'urdf', 'my_robot.urdf.xacro')
   
    user_home = os.path.expanduser('~')

    src_config_path = os.path.join(user_home, 'LAB4', 'src', pkg_name, 'rviz', 'config.rviz')

    if os.path.exists(src_config_path):
        rviz_config_file = src_config_path
        print(f"\033[92m[INFO] Using Source RViz Config: {rviz_config_file}\033[0m")
    else:
        rviz_config_file = os.path.join(pkg_share, 'rviz', 'config.rviz')
        print(f"\033[93m[WARN] Source config not found. Using Installed RViz Config: {rviz_config_file}\033[0m")


    robot_desc = Command(['xacro ', urdf_file])

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_desc}]
        ),
        
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_file]
        ),

        Node(
            package=pkg_name,
            executable='workspace_node.py', 
            name='workspace_visualizer'
        ),

        Node(
            package=pkg_name,
            executable='random_pose_node.py',
            name='random_pose',
            output='screen'
        ),

        Node(
            package=pkg_name,
            executable='controller_node.py',
            name='controller',
            output='screen'
        ),
    ])
