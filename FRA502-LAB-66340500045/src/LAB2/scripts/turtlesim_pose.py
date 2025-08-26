#!/usr/bin/python3

from LAB2.dummy_module import dummy_function, dummy_var
import rclpy
import numpy as np
import math
from tf2_ros import TransformBroadcaster
from nav_msgs.msg import Odometry
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist,Point,TransformStamped
from rclpy.node import Node
from std_srvs.srv import Empty
from std_msgs.msg import Bool,Int16
from turtlesim_plus_interfaces.srv import GivePosition
from tf_transformations import quaternion_from_euler

class PoseNode(Node):
    def __init__(self):
        super().__init__('pose_node')
        self.create_subscription(Pose,'turtle1/pose',self.pose_callback,10)
        self.create_subscription(Pose,'turtle2/pose',self.pose_callback2,10)
        self.odom_publisher = self.create_publisher(Odometry,'/odom',10)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.robot_pose = np.array([0.0,0.0,0.0])
        self.robot_pose1 = np.array([0.0,0.0,0.0])


    def pose_callback(self,msg):
        #  print(msg)
         self.robot_pose[0] = msg.x
         self.robot_pose[1] = msg.y
         self.robot_pose[2] = msg.theta

         odom_msg = Odometry()
         odom_msg.header.stamp = self.get_clock().now().to_msg()
         odom_msg.header.frame_id = "odom"
         odom_msg.child_frame_id = "robot"

         odom_msg.pose.pose.position.x = self.robot_pose[0]
         odom_msg.pose.pose.position.y = self.robot_pose[1]

         q = quaternion_from_euler(0,0,self.robot_pose[2])
         odom_msg.pose.pose.orientation.x = q[0]
         odom_msg.pose.pose.orientation.y = q[1]
         odom_msg.pose.pose.orientation.z = q[2]
         odom_msg.pose.pose.orientation.w = q[3]

         self.odom_publisher.publish(odom_msg)
         t = TransformStamped()
         t.header.stamp = self.get_clock().now().to_msg()
         t.header.frame_id = 'odom'
         t.child_frame_id = 'robot'

         t.transform.translation.x = self.robot_pose[0]-5.4
         t.transform.translation.y = self.robot_pose[1]-5.4
         t.transform.rotation.x = q[0]
         t.transform.rotation.y = q[1]
         t.transform.rotation.z = q[2]
         t.transform.rotation.w = q[3]
        #  print(self.robot_pose)
         self.tf_broadcaster.sendTransform(t)
    def pose_callback2(self,msg):
        #  print(msg)
         self.robot_pose1[0] = msg.x
         self.robot_pose1[1] = msg.y
         self.robot_pose1[2] = msg.theta

         odom_msg = Odometry()
         odom_msg.header.stamp = self.get_clock().now().to_msg()
         odom_msg.header.frame_id = "odom"
         odom_msg.child_frame_id = "robot1"

         odom_msg.pose.pose.position.x = self.robot_pose1[0]
         odom_msg.pose.pose.position.y = self.robot_pose1[1]

         q = quaternion_from_euler(0,0,self.robot_pose1[2])
         odom_msg.pose.pose.orientation.x = q[0]
         odom_msg.pose.pose.orientation.y = q[1]
         odom_msg.pose.pose.orientation.z = q[2]
         odom_msg.pose.pose.orientation.w = q[3]

         self.odom_publisher.publish(odom_msg)
         t = TransformStamped()
         t.header.stamp = self.get_clock().now().to_msg()
         t.header.frame_id = 'odom'
         t.child_frame_id = 'robot1'

         t.transform.translation.x = self.robot_pose1[0]-5.4
         t.transform.translation.y = self.robot_pose1[1]-5.4
         t.transform.rotation.x = q[0]
         t.transform.rotation.y = q[1]
         t.transform.rotation.z = q[2]
         t.transform.rotation.w = q[3]
        #  print(self.robot_pose)
         self.tf_broadcaster.sendTransform(t)
def main(args=None):
    rclpy.init(args=args)
    node = PoseNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()
