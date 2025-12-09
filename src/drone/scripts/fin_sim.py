#!/usr/bin/python3

import rclpy
import math
from rclpy.node import Node
from tf2_msgs.msg import TFMessage
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped

class FinPoseNode(Node):
    def __init__(self):
        super().__init__('fin_pose_node')
        
        self.tf_broadcaster = TransformBroadcaster(self)
        
        self.create_subscription(TFMessage, "/tf", self.tf_callback, 10)
        
        self.get_logger().info('Fin Pose Started! Waiting for data from /tf ...')

        # เก็บ pose ของครีบแต่ละอัน
        self.fin_poses = {
            'fin_1': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'angle': 0.0},
            'fin_2': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'angle': 0.0},
            'fin_3': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'angle': 0.0},
            'fin_4': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'angle': 0.0}
        }

    def tf_callback(self, msg):
        for t in msg.transforms:
            child_frame = t.child_frame_id
            
            if child_frame in self.fin_poses:
                tx = t.transform.translation.x
                ty = t.transform.translation.y
                tz = t.transform.translation.z
                
                angle = math.atan2(ty, tx)
                
                self.fin_poses[child_frame] = {
                    'x': tx,
                    'y': ty,
                    'z': tz,
                    'angle': angle
                }
                
                self.pub_fin_tf(child_frame)

    def pub_fin_tf(self, fin_name):
        pose = self.fin_poses[fin_name]
        
        t = TransformStamped()
        
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'body_drone'
        t.child_frame_id = f'{fin_name}_link'

        t.transform.translation.x = pose['x']
        t.transform.translation.y = pose['y']
        t.transform.translation.z = pose['z']

        qx, qy, qz, qw = self.quaternion_from_euler(0.0, pose['angle'], 0.0)
        t.transform.rotation.x = qx
        t.transform.rotation.y = qy
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw

        self.tf_broadcaster.sendTransform(t)

    def quaternion_from_euler(self, roll, pitch, yaw):
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        qw = cr * cp * cy + sr * sp * sy
        qx = sr * cp * cy - cr * sp * sy
        qy = cr * sp * cy + sr * cp * sy
        qz = cr * cp * sy - sr * sp * cy

        return qx, qy, qz, qw

def main(args=None):
    rclpy.init(args=args)
    node = FinPoseNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()