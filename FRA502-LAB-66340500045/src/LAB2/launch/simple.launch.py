from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim_plus',
            namespace='',
            executable='turtlesim_plus_node.py',
            name='turtlesim'
        ),
        Node(
            package='LAB2',
            namespace='linear',
            executable='eater.py',
            name='eater_node'
        ),
        Node(
            package='LAB2',
            namespace='angular',
            executable='killer.py',
            name='killer_node'
        ),

    ])