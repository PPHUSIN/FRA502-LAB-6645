from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess,DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
def generate_launch_description():
    launch_description = LaunchDescription()
    rate_launch_arg = DeclareLaunchArgument(
        'sampling_frequency',
        default_value='100.0'
    )
    launch_description.add_action(rate_launch_arg)

    turtlesim_node = Node(
            package='turtlesim_plus',
            namespace='',
            executable='turtlesim_plus_node.py',
            name='turtlesim',
        )
    launch_description.add_action(turtlesim_node)
    package_name = 'lab3'
    executable_name = ''
    namespace = ['eater','killer']
    for name in namespace:
        noise_gen = Node(
            package=package_name,
            namespace='',
            executable=name + '.py',
            name=name + '_node',
            parameters=[
                {'sampling_frequency':100.0},{'name':'Mungmond'+name}
            ]
        )
        launch_description.add_action(noise_gen)
    return launch_description