#!/usr/bin/python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Vector3
import sys, select, termios, tty

msg = """
---------------------------------------
   Teleop Jog Keyboard for 3R Robot
---------------------------------------
Moving around:
   w : +X (Forward)
   s : -X (Backward)
   a : +Y (Left)
   d : -Y (Right)
   q : +Z (Up)
   e : -Z (Down)

   f : Toggle Frame (World <-> End-Effector)
   space : Stop all motion
   CTRL-C : Quit

"""

class TeleopNode(Node):
    def __init__(self):
        super().__init__('teleop_sim_node')
        self.publisher_cmd = self.create_publisher(Vector3, '/drone/velocity_setpoint', 10)
        self.settings = termios.tcgetattr(sys.stdin)
        
        self.speed = 1.0 # m/s

    def getKey(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)

            # self.get_logger().info(f"bottone : {key}")
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def run(self):
        print(msg)

        try:
            while True:
                key = self.getKey()
                
                target_vx = 0.0
                target_vy = 0.0
                target_vz = 0.0
                
                if key == 'w':
                    target_vx = self.speed
                elif key == 's':
                    target_vx = -self.speed
                elif key == 'a':
                    target_vy = self.speed
                elif key == 'd':
                    target_vy = -self.speed
                elif key == ' ':
                    target_vz = self.speed
                elif key == 'c':
                    target_vz = -self.speed

                elif key == '\x03':
                    break
                
                twist = Vector3()
                twist.x = target_vx
                twist.y = target_vy
                twist.z = target_vz

                self.publisher_cmd.publish(twist)
                
        except Exception as e:
            print(e)

        finally:
            twist = Vector3()
            self.publisher_cmd.publish(twist)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)

def main(args=None):
    rclpy.init(args=args)
    node = TeleopNode()
    node.run()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()