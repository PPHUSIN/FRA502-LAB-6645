#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Twist, PoseStamped
from std_msgs.msg import String 
from lab4_robot_interface.srv import SetRobotMode, GetTarget
import roboticstoolbox as rtb
import numpy as np
from spatialmath import SE3, UnitQuaternion

class ControllerNode(Node):
    def __init__(self):
        super().__init__('controller_node')
        
        urdf_path = '/home/ppx/LAB4/src/lab4_robot_description/urdf/my_robot.urdf.xacro'
        try:
            self.robot = rtb.ERobot.URDF(urdf_path)
            self.get_logger().info(f"Loaded: {self.robot.name}")
        except Exception as e: return

        self.srv = self.create_service(SetRobotMode, 'set_mode', self.handle_set_mode)
        self.auto_client = self.create_client(GetTarget, 'get_random_target')

        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.singularity_pub = self.create_publisher(String, '/singularity_warning', 10)

        self.current_mode = 0 
        self.target_pose = None 
        self.teleop_frame = 0 
        self.current_q = np.array([0.0, 0.5, -0.5]) 
        
        self.target_twist = Twist() 
        self.current_twist = Twist() 

        self.auto_state = 0   
        self.auto_traj = []   
        self.auto_step = 0    

        self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        
        self.dt = 0.01
        self.create_timer(self.dt, self.control_loop)
        
        self.get_logger().info("Controller Ready!")

    def cmd_vel_callback(self, msg): self.target_twist = msg

    def handle_set_mode(self, request, response):
        self.get_logger().info(f"Mode Request: {request.mode}")
        
        self.target_twist = Twist()
        self.current_twist = Twist()

        if request.mode == 1:
            self.current_mode = 1
            
            x = request.target_pose.position.x
            y = request.target_pose.position.y
            z = request.target_pose.position.z
            qw = request.target_pose.orientation.w
            qx = request.target_pose.orientation.x
            qy = request.target_pose.orientation.y
            qz = request.target_pose.orientation.z
            
            try:
                T_target = SE3(x, y, z) * UnitQuaternion([qw, qx, qy, qz]).SE3()
            except ValueError:
                self.get_logger().warn("Invalid Quaternion, using position only.")
                T_target = SE3(x, y, z)

            sol = self.robot.ikine_LM(T_target, q0=self.current_q, mask=[1, 1, 1, 0, 0, 0], end='tip_frame')
            
            if sol.success:
                response.success = True
                response.message = "IPK Success"
                response.configuration = sol.q.tolist()
                
                self.current_q = sol.q 
                self.get_logger().info(f"IPK Found! Moving to: {sol.q}")
            else:
                response.success = False
                response.message = "IPK Failed: No Solution"
                response.configuration = []
                
                self.get_logger().warn("IPK Failed! Robot stays put.")

        elif request.mode == 2:
            self.current_mode = 2
            self.teleop_frame = request.teleop_frame
            response.success = True
            response.message = f"Switched to Teleop (Frame {self.teleop_frame})"
            
        elif request.mode == 3: 
            self.current_mode = 3
            self.auto_state = 0
            response.success = True
            response.message = "Switched to Auto Mode"
            
        else:
            self.current_mode = 0
            response.success = False
            response.message = "Invalid Mode"
            
        return response

    def control_loop(self):
        if np.allclose(self.current_q, 0, atol=0.05):
            self.current_q = np.array([0.0, 0.5, -0.5])

        if self.current_mode == 2: self.process_teleop_mode()
        elif self.current_mode == 3: self.process_auto_mode()

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['joint_1', 'joint_2', 'joint_3']
        msg.position = self.current_q.tolist()
        self.joint_pub.publish(msg)

    def process_teleop_mode(self):
        a = 0.05 
        self.current_twist.linear.x = (1-a)*self.current_twist.linear.x + a*self.target_twist.linear.x
        self.current_twist.linear.y = (1-a)*self.current_twist.linear.y + a*self.target_twist.linear.y
        self.current_twist.linear.z = (1-a)*self.current_twist.linear.z + a*self.target_twist.linear.z
        self.current_twist.angular.x = (1-a)*self.current_twist.angular.x + a*self.target_twist.angular.x
        self.current_twist.angular.y = (1-a)*self.current_twist.angular.y + a*self.target_twist.angular.y
        self.current_twist.angular.z = (1-a)*self.current_twist.angular.z + a*self.target_twist.angular.z

        gain = 5.0
        v = np.array([
            self.current_twist.linear.x, 
            self.current_twist.linear.y, 
            self.current_twist.linear.z,
            self.current_twist.angular.x, 
            self.current_twist.angular.y, 
            self.current_twist.angular.z
        ]) * gain 

        if np.linalg.norm(v) < 0.001: return

        J = self.robot.jacob0(self.current_q, end='tip_frame')
        if self.teleop_frame == 0:
            T = self.robot.fkine(self.current_q, end='tip_frame')
            v[:3] = T.R @ v[:3]; v[3:] = T.R @ v[3:]

        J_linear = J[:3, :]
        manipulability = np.abs(np.linalg.det(J_linear))
        
        status_msg = f"Status: OK | Val: {manipulability:.5f}"
        
        if manipulability < 0.001:
            warning_msg = f"SINGULARITY! Stopping. Val={manipulability:.5f}"
            self.get_logger().warn(warning_msg)
            self.singularity_pub.publish(String(data=warning_msg))
            return 

        self.singularity_pub.publish(String(data=status_msg))

        J_pinv = np.linalg.pinv(J, rcond=0.05)
        q_dot = J_pinv @ v
        
        new_q = self.current_q + (q_dot * self.dt)

        z = self.robot.fkine(new_q, end='tip_frame').t[2]
        if z < 0.0:
            self.get_logger().warn(f"STOP: Ground Collision! z={z:.2f}")
            self.singularity_pub.publish(String(data="Warning: Ground Collision!"))
            return 

        if self.robot.qlim is not None:
             if not (np.all(new_q >= self.robot.qlim[0,:]) and np.all(new_q <= self.robot.qlim[1,:])): return

        self.current_q = new_q

    def process_auto_mode(self):
        if self.auto_state == 0:
            if not self.auto_client.wait_for_service(timeout_sec=1.0): return
            req = GetTarget.Request()
            future = self.auto_client.call_async(req)
            future.add_done_callback(self.auto_response_callback)
            self.auto_state = 1

        elif self.auto_state == 2: 
            if self.auto_step < len(self.auto_traj):
                self.current_q = self.auto_traj[self.auto_step]
                self.auto_step += 1
            else:
                self.auto_state = 0 

    def auto_response_callback(self, future):
        try:
            res = future.result()
            if res.success:
                p = res.target_pose.position
                T = SE3(p.x, p.y, p.z)
                sol = self.robot.ikine_LM(T, q0=self.current_q, mask=[1,1,1,0,0,0], end='tip_frame')
                if sol.success:
                    traj = rtb.jtraj(self.current_q, sol.q, 1000)
                    self.auto_traj = traj.q
                    self.auto_step = 0
                    self.auto_state = 2 
                else:
                    self.auto_state = 0 
        except Exception as e:
            self.auto_state = 0

def main(args=None):
    rclpy.init(args=args)
    node = ControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()