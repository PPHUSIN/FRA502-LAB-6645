#!/usr/bin/python3

from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import Command
import os

def generate_launch_description():

    pkg_name = 'drone'
    pkg_path = get_package_share_directory(pkg_name)

    urdf_path = os.path.join(pkg_path, "URDF", "drone.urdf.xacro")

    robot_description = ParameterValue(
        Command(['xacro', ' ', urdf_path]),
        value_type=str
    )

    robot_state_pub = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}],
        output="screen"
    )

    joint_state_pub = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        parameters=[{
            "robot_description": robot_description,
            "source_list": ["/fin_states"]
        }],
        output="screen"
    )

    rviz_config = os.path.join(pkg_path, "config", "display.rviz")
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz_config],
        output="screen"
    )

    drone_pose_sim_node = Node(
        package=pkg_name,
        executable="drone_pose_sim.py",
        name='drone_pose_sim_node',
        output="screen"
    )

    fin_sim_node = Node(
        package=pkg_name,
        executable="fin_sim.py",
        name='fin_sim_node',
        output="screen"
    )

    drone_pose_node = Node(
        package=pkg_name,
        executable="drone_pose.py",
        name='drone_pose_node',
        output="screen"
    )

    fin_angle_node = Node(
        package=pkg_name,
        executable="fin_angle.py",
        name='fin_angle_node',
        output="screen"
    )

    return LaunchDescription([
        joint_state_pub,
        robot_state_pub,
        rviz,
        drone_pose_sim_node,
        fin_sim_node
        # drone_pose_node,
        # fin_angle_node
    ])
