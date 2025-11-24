#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Pose
from lab4_robot_interface.srv import GetTarget
import random

class RandomPoseNode(Node):
    def __init__(self):
        super().__init__('random_pose')
        
        self.srv = self.create_service(GetTarget, 'get_random_target', self.handle_get_target)
        self.target_pub = self.create_publisher(PoseStamped, '/target', 10)
        
        self.current_target = self.generate_random_pose()
        
        self.create_timer(0.1, self.publish_target)
        self.get_logger().info("Random Pose Node Started!")

    def generate_random_pose(self):
        p = Pose()
        p.position.x = random.uniform(0.1, 0.3)
        p.position.y = random.uniform(-0.3, 0.3)
        p.position.z = random.uniform(0.1, 0.4)
        p.orientation.w = 1.0
        return p

    def handle_get_target(self, request, response):
        self.current_target = self.generate_random_pose()
        response.success = True
        response.target_pose = self.current_target
        self.get_logger().info(f"New Target Generated: {self.current_target.position.x:.2f}")
        return response

    def publish_target(self):
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "world"
        msg.pose = self.current_target
        self.target_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = RandomPoseNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()