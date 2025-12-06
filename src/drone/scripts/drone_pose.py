#!/usr/bin/python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped, Twist
from std_msgs.msg import Float64MultiArray
from nav_msgs.msg import Odometry

class DroneBridgeNode(Node):

    def __init__(self):
        super().__init__('drone_pose_node')

        self.tf_broadcaster = TransformBroadcaster(self)

        # self.create_subscription(Float64MultiArray, '/drone/angle', self.angle_callback, 10)
        # self.create_subscription(Twist, "/drone_velo", self.Drone_Velo_callback, 10)
        # self.create_subscription(Twist, "/cmd_vel", self.Drone_Velo_callback, 10)
        self.create_subscription(Odometry, "/odom", self.drone_pose_callback, 10)
        
        self.get_logger().info('Drone Pose Started! Waiting for data from /drone/pose ...')

        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0

        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0

        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        self.rx = 0.0
        self.ry = 0.0
        self.rz = 0.0

        self.timer = self.create_timer(0.01, self.pub_timer)

        # self.dt = 0.01

    def drone_pose_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        self.z = msg.pose.pose.position.z

        self.roll = msg.twist.twist.angular.x
        self.pitch = msg.twist.twist.angular.y
        self.yaw = msg.twist.twist.angular.z

    # def Drone_Velo_callback(self, msg):
    #     self.vx = msg.linear.x
    #     self.vy = msg.linear.y
    #     self.vz = msg.linear.z

    #     self.roll = msg.angular.x
    #     self.pitch = msg.angular.y
    #     self.yaw = msg.angular.z

    # def cal_pose(self):
    #     self.x += self.vx * self.dt
    #     self.y += self.vy * self.dt
    #     self.z += self.vz * self.dt

    #     self.rx += self.roll * self.dt
    #     self.ry += self.pitch * self.dt
    #     self.rz += self.yaw * self.dt

    #     self.pub_tf()

    # def angle_callback(self, msg):
    #     self.roll = msg.data[0]
    #     self.pitch = msg.data[1]
    #     self.yaw = msg.data[2]

    def pub_tf(self):

        t = TransformStamped()

        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'base_link'
        t.child_frame_id = 'body_drone'

        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = self.z

        t.transform.rotation.x = self.roll
        t.transform.rotation.y = self.pitch
        t.transform.rotation.z = self.yaw
        t.transform.rotation.w = 1.0

        self.tf_broadcaster.sendTransform(t)

    # def listener_callback(self, msg):
        
    #     t = TransformStamped()

    #     t.header.stamp = self.get_clock().now().to_msg()
    #     t.header.frame_id = 'base_link'
    #     t.child_frame_id = 'body_drone'

    #     t.transform.translation.x = msg.pose.position.x
    #     t.transform.translation.y = msg.pose.position.y
    #     t.transform.translation.z = msg.pose.position.z

    #     t.transform.rotation.x = msg.pose.orientation.x
    #     t.transform.rotation.y = msg.pose.orientation.y
    #     t.transform.rotation.z = msg.pose.orientation.z
    #     t.transform.rotation.w = msg.pose.orientation.w

    #     self.tf_broadcaster.sendTransform(t)

    def pub_timer(self):
        self.pub_tf()
        # self.cal_pose()

def main(args=None):
    rclpy.init(args=args)
    node = DroneBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()