#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField, JointState
from geometry_msgs.msg import PoseStamped
import struct
import numpy as np
import roboticstoolbox as rtb 

import os
from ament_index_python.packages import get_package_share_directory

class WorkspaceNode(Node):
    def __init__(self):
        super().__init__('workspace_visualizer')
        
        package_name = 'lab4_robot_description'
        urdf_file = 'my_robot.urdf.xacro'
        
        try:
            pkg_share = get_package_share_directory(package_name)
            urdf_path = os.path.join(pkg_share, 'urdf', urdf_file)
            
            self.get_logger().info(f"Loading URDF from: {urdf_path}")
            self.robot = rtb.ERobot.URDF(urdf_path)
            self.get_logger().info(f'Loaded robot: {self.robot.name}')
        except Exception as e:
            self.get_logger().error(f"Failed to load robot: {e}")
            return

        self.ws_pub = self.create_publisher(PointCloud2, '/workspace_cloud', 10)
        self.ee_pub = self.create_publisher(PoseStamped, '/end_effector', 10)
        
        self.create_subscription(JointState, '/joint_states', self.joint_callback, 10)
        self.current_q = np.zeros(self.robot.n)

        self.create_timer(2.0, self.publish_workspace) 
        self.create_timer(0.1, self.publish_end_effector) 

    def joint_callback(self, msg):
        if len(msg.position) >= self.robot.n:
             self.current_q = np.array(msg.position[:self.robot.n])

    def publish_workspace(self):
        points = []
        num_samples = 2000 
        q_lim = self.robot.qlim 
        
        for _ in range(num_samples):
            if q_lim is not None:
                 q_rand = np.random.uniform(q_lim[0, :], q_lim[1, :])
            else:
                 q_rand = np.random.uniform(-3.14, 3.14, 3) 

            T = self.robot.fkine(q_rand, end='tip_frame')
            x, y, z = T.t[0], T.t[1], T.t[2]
            
            if z < 0.0: continue 

            pt_data = struct.pack('fff', x, y, z)
            points.append(pt_data)

        msg = PointCloud2()
        msg.header.frame_id = "world" 
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.height = 1
        msg.width = len(points)
        msg.fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1)
        ]
        msg.is_bigendian = False
        msg.point_step = 12
        msg.row_step = 12 * len(points)
        msg.is_dense = True
        msg.data = b''.join(points)
        self.ws_pub.publish(msg)

    def publish_end_effector(self):
        T_now = self.robot.fkine(self.current_q, end='tip_frame')
        
        ee_msg = PoseStamped()
        ee_msg.header.frame_id = "world"
        ee_msg.header.stamp = self.get_clock().now().to_msg()
        ee_msg.pose.position.x = T_now.t[0]
        ee_msg.pose.position.y = T_now.t[1]
        ee_msg.pose.position.z = T_now.t[2]
        ee_msg.pose.orientation.w = 1.0 
        
        self.ee_pub.publish(ee_msg)

def main(args=None):
    rclpy.init(args=args)
    node = WorkspaceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()