#!/usr/bin/python3

from LAB2.dummy_module import dummy_function, dummy_var
import rclpy
import numpy as np
import math
from tf2_ros import TransformBroadcaster
from nav_msgs.msg import Odometry
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist,Point,TransformStamped,PoseStamped
from rclpy.node import Node
from std_srvs.srv import Empty
from std_msgs.msg import Bool,Int16
from turtlesim_plus_interfaces.srv import GivePosition
from tf_transformations import quaternion_from_euler


class EaterNode(Node):
    def __init__(self):
        super().__init__('eater_node')
        self.cmd_vel_pub = self.create_publisher(Twist,'/turtle1/cmd_vel',10)
        self.check_pub = self.create_publisher(Bool,'/check',10)
        self.create_subscription(Pose,'turtle1/pose',self.pose_callback,10)
        self.create_subscription(Point,'mouse_position',self.mouse_callback,10)
        self.create_subscription(PoseStamped,'goal_pose',self.goalpose,10)
        self.create_timer(0.01 , self.timer_callback )
        self.spawn_pizza_client = self.create_client(GivePosition, 'spawn_pizza')
        self.eat_pizza_client =self.create_client(Empty,'turtle1/eat')
        self.robot_pose = np.array([0.0,0.0,0.0])
        self.mouse_pose = np.array([0.0,0.0])
        self.goal_pose = np.array([0.0,0.0])
        self.control_robot = np.array([0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
        self.pizza = []
        self.de = True
        self.c = 0
        self.count = 0
        self.m = 0
    def eat_pizza(self):
         eat_request = Empty.Request()
         self.eat_pizza_client.call_async(eat_request)
    def spawn_pizza(self,x,y):
         position_requst = GivePosition.Request()
         position_requst.x = x
         position_requst.y = y 
         self.spawn_pizza_client.call_async(position_requst)
    def goalpose(self,msg):
         self.goal_pose[0] = msg.pose.position.x+5.4
         self.goal_pose[1] = msg.pose.position.y+5.4
         if self.m < 5 :
            self.spawn_pizza(self.goal_pose[0] ,self.goal_pose[1] )
            self.pizza.append((self.goal_pose[0] ,self.goal_pose[1] ))
            self.m+=1
         self.count += 1
         print(self.goal_pose)
    def mouse_callback(self,msg):
        #  print(msg)
         self.mouse_pose[0] = msg.x
         self.mouse_pose[1] = msg.y
         if self.m < 5 :
            self.spawn_pizza(self.mouse_pose[0] ,self.mouse_pose[1] )
            self.pizza.append((self.mouse_pose[0] ,self.mouse_pose[1] ))
            self.m+=1
         self.count += 1
    def pose_callback(self,msg):
        #  print(msg)
         self.robot_pose[0] = msg.x
         self.robot_pose[1] = msg.y
         self.robot_pose[2] = msg.theta

    def control(self):
        msg = Bool()
        if self.c == 5:
                msg.data = True
                self.de = False
        if self.count > 0 :
            if (5 - self.c > 0) :
                msg.data = False
                self.control_robot[0] = self.pizza[self.c ][0] - self.robot_pose[0] #delta_x
                self.control_robot[1] = self.pizza[self.c ][1] - self.robot_pose[1] #delta_y
            else:
                self.control_robot[0] = self.mouse_pose[0] - self.robot_pose[0] #delta_x
                self.control_robot[1] = self.mouse_pose[1] - self.robot_pose[1] #delta_y
            self.control_robot[2] = math.atan2(self.control_robot[1],self.control_robot[0]) #theta
            self.control_robot[3] = math.sqrt((self.control_robot[0]**2)+(self.control_robot[1]**2)) -1.0 #d
            t = self.control_robot[2] - self.robot_pose[2]#ethetha
            self.control_robot[7] = math.atan2(math.sin(t),math.cos(t))#ethetha
            self.control_robot[5] = (5)*(self.control_robot[3])
            self.control_robot[6] = (20)*(self.control_robot[7])
            self.cmdvel(self.control_robot[5] ,self.control_robot[6])
            # print(self.c)
        if self.control_robot[5] <= 0.6 :
             self.c += 1
             self.count -= 1
        # print(self.c)
        self.check_pub.publish(msg)
    def cmdvel(self,v,w):
            msg = Twist()
            msg.linear.x = v
            msg.angular.z = w
            self.cmd_vel_pub.publish(msg)
    def timer_callback(self):
            if self.count > 0  :
                self.control()
            else :
                self.cmdvel(0.0,0.0)
            if self.de :
                self.eat_pizza()
def main(args=None):
    rclpy.init(args=args)
    node = EaterNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()
