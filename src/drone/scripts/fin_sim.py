#!/usr/bin/python3

import rclpy
import math
from rclpy.node import Node
from sensor_msgs.msg import JointState
from tf2_msgs.msg import TFMessage 

class FinAngleNode(Node):
    def __init__(self):
        super().__init__('fin_pos_listener')
        
        self.create_subscription(TFMessage, "/tf", self.tf_callback, 10)
        self.angle_pub = self.create_publisher(JointState, "/fin_states", 10)

        self.fin_values = {
            'fin_1': 0.0,
            'fin_2': 0.0,
            'fin_3': 0.0,
            'fin_4': 0.0
        }

    def tf_callback(self, msg):
        updated = False
        
        for t in msg.transforms:
            child_frame = t.child_frame_id
            
            if child_frame in self.fin_values:
                
                tx = t.transform.translation.x
                ty = t.transform.translation.y
                tz = t.transform.translation.z

                value = math.atan2(ty, tx) 

                self.fin_values[child_frame] = value
                updated = True

        if updated:
            self.publish_joints()

    def publish_joints(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "body_drone"

        msg.name = ["fin_1_joint", "fin_2_joint", "fin_3_joint", "fin_4_joint"]
        
        msg.position = [
            self.fin_values['fin_1'],
            self.fin_values['fin_2'],
            self.fin_values['fin_3'],
            self.fin_values['fin_4']
        ]

        self.angle_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = FinAngleNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__=='__main__':
    main()