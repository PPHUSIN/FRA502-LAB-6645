#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys, select, termios, tty

msg = """
-------------------------------------------------
      Teleop Jog Keyboard 
-------------------------------------------------
    [Linear Velocity]        [Angular Velocity]
           w (x+)                   i (pitch+)
     a (y+) s (x-) d (y-)     j (yaw+) k (pitch-) l (yaw-)
           q (z+)                   u (roll+)
           e (z-)                   o (roll-)
-------------------------------------------------
"""

class TeleopNode(Node):
    def __init__(self):
        super().__init__('teleop_jog_keyboard')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.speed = 0.5       
        self.turn_speed = 1.0  

    def getKey(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist: key = sys.stdin.read(1)
        else: key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        return key

    def run(self):
        print(msg)
        try:
            while True:
                key = self.getKey()
                twist = Twist()
                
                if key == 'w': twist.linear.x = self.speed
                elif key == 's': twist.linear.x = -self.speed
                elif key == 'a': twist.linear.y = self.speed
                elif key == 'd': twist.linear.y = -self.speed
                elif key == 'q': twist.linear.z = self.speed
                elif key == 'e': twist.linear.z = -self.speed

                elif key == 'u': twist.angular.x = self.turn_speed
                elif key == 'o': twist.angular.x = -self.turn_speed
                elif key == 'i': twist.angular.y = self.turn_speed
                elif key == 'k': twist.angular.y = -self.turn_speed
                elif key == 'j': twist.angular.z = self.turn_speed
                elif key == 'l': twist.angular.z = -self.turn_speed

                elif key == ' ': pass
                elif key == '\x03': break

                self.pub.publish(twist)
        except Exception as e: print(e)
        finally: self.pub.publish(Twist())

def main(args=None):
    global settings
    settings = termios.tcgetattr(sys.stdin)
    rclpy.init(args=args)
    node = TeleopNode()
    node.run()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()