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
from std_msgs.msg import Bool
from turtlesim.srv import Spawn,Kill
from turtlesim_plus_interfaces.srv import GivePosition
from tf_transformations import quaternion_from_euler

class KillerNode(Node):
    def __init__(self):
        super().__init__('killer_node')
        self.cmd_vel_pub = self.create_publisher(Twist,'/turtle2/cmd_vel',10)
        self.create_subscription(Pose,'turtle1/pose',self.pose_callback1,10)
        self.create_subscription(Pose,'turtle2/pose',self.pose_callback2,10)
        self.create_subscription(Bool,'/check',self.start,10)
        self.create_timer(0.01 , self.timer_callback )
        self.spawn_turtle_client = self.create_client(Spawn, 'spawn_turtle')
        self.eat_turtle_client =self.create_client(Kill,'remove_turtle')
        self.robot_pose = np.array([0.0,0.0,0.0])
        self.robot_pose2 = np.array([0.0,0.0,0.0])
        self.mouse_pose = np.array([0.0,0.0])
        self.control_robot = np.array([0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
        self.spawn_turtle()
        self.check = False
    def spawn_turtle(self):
         position_requst = Spawn.Request()
         position_requst.x = 2.0
         position_requst.y = 2.0
         self.spawn_turtle_client.call_async(position_requst)
    def killer_turtle(self):
         eat_request = Kill.Request()
         eat_request.name = 'turtle1'
         self.eat_turtle_client .call_async(eat_request)
    def pose_callback1(self,msg):
        #  print(msg)
         self.robot_pose[0] = msg.x
         self.robot_pose[1] = msg.y
         self.robot_pose[2] = msg.theta
         print(self.robot_pose)
    def pose_callback2(self,msg):
        #  print(msg)
         self.robot_pose2[0] = msg.x
         self.robot_pose2[1] = msg.y
         self.robot_pose2[2] = msg.theta  
         print(self.robot_pose2)
    def start(self,msg):
         self.check = msg.data
    def control(self):
        self.control_robot[0] = self.robot_pose[0]  - self.robot_pose2[0] #delta_x
        self.control_robot[1] = self.robot_pose[1] - self.robot_pose2[1] #delta_y
        self.control_robot[2] = math.atan2(self.control_robot[1],self.control_robot[0]) #theta
        self.control_robot[3] = math.sqrt((self.control_robot[0]**2)+(self.control_robot[1]**2)) -1.0 #d
        t = self.control_robot[2] - self.robot_pose2[2]#ethetha
        self.control_robot[7] = math.atan2(math.sin(t),math.cos(t))#ethetha
        self.control_robot[5] = (5)*(self.control_robot[3])
        self.control_robot[6] = (10)*(self.control_robot[7])
        self.cmdvel(self.control_robot[5] ,self.control_robot[6])
        if self.control_robot[3] <= 0.5 :
             self.killer_turtle()
    def cmdvel(self,v,w):
            msg = Twist()
            msg.linear.x = v
            msg.angular.z = w
            self.cmd_vel_pub.publish(msg)
    def timer_callback(self):
            if (self.check):
                self.control()
def main(args=None):
    rclpy.init(args=args)
    node = KillerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()
