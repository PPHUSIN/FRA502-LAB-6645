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
            package='lab3',
            namespace='',
            executable='eater.py',
            name='eater_node',
            parameters=[
                {'sampling_frequency':100.0}
            ]
        ),
        Node(
            package='lab3',
            namespace='',
            executable='killer.py',
            name='killer_node',
            parameters=[
                {'sampling_frequency':100.0}
            ]
        ),

    ])