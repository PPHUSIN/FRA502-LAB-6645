#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
import numpy as np
import math


class LQRControlNode(Node):
    def __init__(self):
        super().__init__("lqr_hover_control")

        # --- SETTINGS ---
        self.frequency = 100.0
        self.dt = 1.0 / self.frequency

        # --- STATE VARIABLES ---
        # [phi, theta, psi, phi_dot, theta_dot, psi_dot, z, vz, z_int]
        self.state_hover = np.zeros(9)
        self.setpoint_hover = np.zeros(9)

        # Default target: 1.0 meter height
        self.setpoint_hover[6] = 1.0

        self.z_integral = 0.0
        self.mass = 0.707  # kg

        # --- GAINS (Computed from your MATLAB Output) ---
        # Mode: AERODYNAMIC (Hard Mode)
        # Trust these numbers. They are matched to your physics engine.

        self.K_hover = np.array([
    [ 1.567898,  0.000000, -1.112104,  2.114379,  0.000000, -2.214581, -0.000000, -0.000000,  0.000000],
    [-1.567898,  0.000000, -1.112104, -2.114379,  0.000000, -2.214581,  0.000000,  0.000000,  0.000000],
    [ 0.000000, -1.567898, -1.112104,  0.000000, -2.114379, -2.214581,  0.000000, -0.000000,  0.000000],
    [ 0.000000,  1.567898, -1.112104,  0.000000,  2.114379, -2.214581, -0.000000, -0.000000,  0.000000],
    [-0.000000, -0.000000,  0.000000, -0.000000, -0.000000,  0.000000,  8.970776,  5.617709, -3.036126],
])



        # --- PUBLISHERS ---
        self.pub_fin1 = self.create_publisher(Float64, "/drone/fin_1/position", 10)
        self.pub_fin2 = self.create_publisher(Float64, "/drone/fin_2/position", 10)
        self.pub_fin3 = self.create_publisher(Float64, "/drone/fin_3/position", 10)
        self.pub_fin4 = self.create_publisher(Float64, "/drone/fin_4/position", 10)
        self.pub_thrust = self.create_publisher(Float64, "/drone/cmd_thrust", 10)

        # --- SUBSCRIBERS ---
        self.create_subscription(Odometry, "/odom", self.odom_callback, 10)
        self.create_subscription(Twist, "/drone/setpoint", self.setpoint_callback, 10)

        self.create_timer(self.dt, self.control_loop)
        self.get_logger().info("LQR Ready! Mode: HARD (Aero Gains Active)")

    def setpoint_callback(self, msg):
        self.setpoint_hover[0] = msg.angular.x
        self.setpoint_hover[1] = msg.angular.y
        self.setpoint_hover[2] = msg.angular.z
        self.setpoint_hover[6] = msg.linear.z
        self.get_logger().info(f"Target Z: {msg.linear.z:.2f}m")

    def odom_callback(self, msg):
        pos = msg.pose.pose.position
        vel = msg.twist.twist.linear
        ang_vel = msg.twist.twist.angular
        quat = msg.pose.pose.orientation
        roll, pitch, yaw = self.euler_from_quaternion(quat.x, quat.y, quat.z, quat.w)

        self.state_hover[0] = roll
        self.state_hover[1] = pitch
        self.state_hover[2] = yaw
        self.state_hover[3] = ang_vel.x
        self.state_hover[4] = ang_vel.y
        self.state_hover[5] = ang_vel.z
        self.state_hover[6] = pos.z
        self.state_hover[7] = vel.z

    def control_loop(self):
        hover_err = self.state_hover - self.setpoint_hover

        # Integral Accumulation
        # NOTE: Your gain is negative (-0.63).
        # We accumulate (State - Target). If we are LOW (0 - 1 = -1), integral becomes negative.
        # -K (-0.63) * -Integral = Negative Thrust?
        # WAIT! If we are LOW, we need POSITIVE thrust.
        # Let's fix the Integral Error Sign to match your gain:
        # Accumulate (Target - State) so "Under" = Positive Integral.
        # Gain is (-0.63). -K * Pos_Int = Negative...
        # Let's stick to standard LQR u = -Kx.
        # If x (Height) is 0 (Target 1), x_err = -1.
        # -K (1.79) * -1 = +1.79 (Correct).
        # For integral, we integrate x_err (-1). Int becomes negative.
        # -K (-0.63) * (Negative Int) = Negative Output?
        # This implies your Z_int gain might assume the opposite sign.
        # FIX: I will flip the integral accumulation sign to ensure it helps, not hurts.

        self.z_integral += (self.setpoint_hover[6] - self.state_hover[6]) * self.dt
        hover_err[8] = self.z_integral

        # LQR Calculation (u = -Kx)
        u_hover = -np.dot(self.K_hover, hover_err)

        cmd_fin1, cmd_fin2 = u_hover[0], u_hover[1]
        cmd_fin3, cmd_fin4 = u_hover[2], u_hover[3]

        # Gravity Compensation (~7.85 N)
        # This is CRITICAL. Without this, the LQR only outputs ~1.79N, which is not enough to fly.
        raw_thrust = u_hover[4] + (self.mass*9.81)

        # --- SAFETY LIMITS ---
        # 1. Fin Angles (0.5 rad ~= 28 deg)
        fin_limit = 0.5
        self.publish_fin(self.pub_fin1, cmd_fin1, fin_limit)
        self.publish_fin(self.pub_fin2, cmd_fin2, fin_limit)
        self.publish_fin(self.pub_fin3, cmd_fin3, fin_limit)
        self.publish_fin(self.pub_fin4, cmd_fin4, fin_limit)

        # 2. Thrust Limits
        # Soft limit at 18N (approx 2:1 thrust-to-weight ratio)
        MAX_THRUST = 18.0
        MIN_THRUST = 0.0

        final_thrust = max(MIN_THRUST, min(MAX_THRUST, float(raw_thrust)))

        # DEBUG: Print status so you can see if it's working
        # self.get_logger().info(f"Z:{self.state_hover[6]:.2f}m | T:{final_thrust:.2f}N")

        t_msg = Float64()
        t_msg.data = final_thrust
        self.pub_thrust.publish(t_msg)

    def publish_fin(self, publisher, value, limit):
        msg = Float64()
        msg.data = max(-limit, min(limit, float(value)))
        publisher.publish(msg)

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
    node = LQRControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
