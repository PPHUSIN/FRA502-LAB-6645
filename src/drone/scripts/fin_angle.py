#!/usr/bin/python3

from drone.dummy_module import dummy_function, dummy_var
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray
# from tf2_ros import TransformBroadcaster

class FinAngleNode(Node):
    def __init__(self):
        super().__init__('fin_angle_node')
        
        self.create_subscription(Float64MultiArray, "/fin_angle", self.Angle_callback, 10)

        self.angle_pub = self.create_publisher(JointState, "/fin_states", 10)

        # self.tf_broadcaster = TransformBroadcaster(self)

        self.fin1 = 0.0
        self.fin2 = 0.0
        self.fin3 = 0.0
        self.fin4 = 0.0

    #     self.create_timer(0.01, self.timer)

    # def timer(self):
    #     self.Fin_Angle_pub()

    def Fin_Angle_pub(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "body_drone"

        msg.name = ["fin_1_joint", "fin_2_joint", "fin_3_joint", "fin_4_joint"]

        msg.position = [self.fin1, self.fin2, self.fin3, self.fin4]

        self.angle_pub.publish(msg)

    def Angle_callback(self, msg):
        self.fin1 = msg.data[0]
        self.fin2 = msg.data[1]
        self.fin3 = msg.data[2]
        self.fin4 = msg.data[3]

        self.Fin_Angle_pub()

def main(args=None):
    rclpy.init(args=args)
    node = FinAngleNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()
