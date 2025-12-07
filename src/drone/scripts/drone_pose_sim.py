#!/usr/bin/python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped, Twist
from nav_msgs.msg import Odometry
import math

class DroneBridgeNode(Node):

    def __init__(self):
        super().__init__('drone_pose_sim_node')

        self.tf_broadcaster = TransformBroadcaster(self)

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

    def drone_pose_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        self.z = msg.pose.pose.position.z

        quat = msg.pose.pose.orientation
        self.roll, self.pitch, self.yaw = self.euler_from_quaternion(quat.x, quat.y, quat.z, quat.w)

        self.pub_tf()

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

    def euler_from_quaternion(self, x, y, z, w):
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)
        return roll_x, pitch_y, yaw_z

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