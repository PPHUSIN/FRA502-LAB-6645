import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_name = 'drone_gazebo'

    # 1. WORLD FILE SETUP
    # We switch this to 'aerodynamics.world' because that is the file we created earlier.
    # If you want an empty world, just comment out the 'world_path' line below.
    world_file_name = 'aerodynamics.world' 
    world_path = os.path.join(get_package_share_directory(pkg_name), 'worlds', world_file_name)

    # 2. PROCESS XACRO (URDF)
    file_subpath = 'urdf/drone.urdf.xacro'
    xacro_file = os.path.join(get_package_share_directory(pkg_name), file_subpath)
    robot_description_raw = xacro.process_file(xacro_file).toxml()

    # 3. NODES & PROCESSES

    # A. Robot State Publisher (Publishes the robot structure)
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_raw,
                     'use_sim_time': True}]
    )

    # B. Gazebo Simulation
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
        launch_arguments={'world': world_path}.items()
    )

    # C. Spawn the Drone
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'my_drone',
                                   '-z', '0.5'],
                        output='screen')

    # D. TVC CONTROLLER (NEW!)
    # Since we put the script in the 'launch' folder, we find it there and run it with Python.
    run_tvc_controller = Node(
        package='drone_gazebo',
        executable='tvc_controller.py',
        output='screen',
        emulate_tty=True
    )

    run_lqr = Node(
        package="drone_gazebo",
        executable="lqr_node.py",
        output="screen",
        emulate_tty=True,
    )

    run_lqr_hover = Node(
        package="drone_gazebo",
        executable="lqr_hover_node.py",
        output="screen",
        emulate_tty=True,
    )
    return LaunchDescription([
        gazebo,
        node_robot_state_publisher,
        spawn_entity,
        run_tvc_controller,
        run_lqr,
        # run_lqr_hover,
    ])
