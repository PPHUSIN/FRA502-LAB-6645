#!/usr/bin/env python3
"""
Minimal LQR Controller with Velocity Mode
==========================================

Position Mode: Direct position setpoint tracking
Velocity Mode: Continuous position setpoint integration from velocity commands

Control Modes:
- POSITION: Direct position setpoint tracking (original behavior)
- VELOCITY: Velocity setpoints integrated to moving position targets
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64, String
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist, PoseStamped, Vector3
import numpy as np
import math


class MinimalLQRController(Node):
    def __init__(self):
        super().__init__("lqr_controller")
        self.frequency = 100.0
        self.dt = 1.0 / self.frequency
        self.mass = 0.707    # Drone mass + 4 fins

        # Control Mode
        self.control_mode = "POSITION"  # "POSITION" or "VELOCITY"

        # States
        self.state_hover = np.zeros(9)
        self.setpoint_hover = np.zeros(9)
        self.setpoint_hover[6] = 1.0

        self.state_pos = np.zeros(6)
        self.setpoint_pos = np.zeros(6)
        self.z_integral = 0.0

        # Velocity Control Variables
        self.velocity_setpoint = np.zeros(2)  # [vx, vy] desired velocities
        self.velocity_enabled = False
        self.last_position_update = self.get_clock().now()

        # USE PROVEN ATTITUDE GAINS
        # Updated K_hover (Snappier response to help braking)
        # Updated K_hover (Stiffer/Faster to reduce lag)
        # Updated K_hover (Inner Loop - High Stiffness)
# Physics: Fin1+ -> Roll+, Fin3+ -> Pitch-
        self.K_hover = np.array([
    [ 2.699202,  0.000000, -1.142010,  0.646371,  0.000000, -0.828742, -0.000000,  0.000000,  0.000000],
    [-2.699202,  0.000000, -1.142010, -0.646371,  0.000000, -0.828742, -0.000000,  0.000000,  0.000000],
    [-0.000000, -2.699202, -1.142010, -0.000000, -0.646371, -0.828742,  0.000000,  0.000000,  0.000000],
    [ 0.000000,  2.699202, -1.142010,  0.000000,  0.646371, -0.828742, -0.000000,  0.000000,  0.000000],
    [ 0.000000, -0.000000, -0.000000,  0.000000, -0.000000, -0.000000,  3.060675,  2.606323, -1.097478],
])

        self.K_pos = np.array([
    [ 0.932965,  0.000000,  1.330181,  0.000000,  0.000000,  0.000000],
    [ 0.000000, -0.932965,  0.000000, -1.330181,  0.000000,  0.000000],
])
        # self.K_pos = np.array( #NEED TO SWAP AXIS FROM MATLAB
        #     [
        #         [+0.10, 0.0, +0.20, 0.0, +0.10, 0.0],  # X: positive (forward/back)
        #         [0.0, -0.10, 0.0, -0.20, 0.0, -0.10],  # Y: negative (Y+ = LEFT)
        #     ]
        # )

        # Publishers
        self.pub_fin1 = self.create_publisher(Float64, "/drone/fin_1/position", 10)
        self.pub_fin2 = self.create_publisher(Float64, "/drone/fin_2/position", 10)
        self.pub_fin3 = self.create_publisher(Float64, "/drone/fin_3/position", 10)
        self.pub_fin4 = self.create_publisher(Float64, "/drone/fin_4/position", 10)
        self.pub_thrust = self.create_publisher(Float64, "/drone/cmd_thrust", 10)

        # Status publisher
        self.pub_status = self.create_publisher(String, "/drone/control_status", 10)

        # Subscribers
        self.create_subscription(Odometry, "/odom", self.odom_callback, 10)
        self.create_subscription(PoseStamped, "/drone/goal", self.goal_callback, 10)
        self.create_subscription(Twist, "/drone/setpoint", self.setpoint_callback, 10)

        # New velocity control subscribers
        self.create_subscription(
            Vector3, "/drone/velocity_setpoint", self.velocity_setpoint_callback, 10
        )
        self.create_subscription(
            String, "/drone/control_mode", self.control_mode_callback, 10
        )

        self.create_timer(self.dt, self.control_loop)
        self.get_logger().info("MINIMAL LQR Controller with Velocity Mode")
        self.get_logger().info("Modes: POSITION (direct) | VELOCITY (integrated)")
        self.get_logger().info(f"Current mode: {self.control_mode}")

    def control_mode_callback(self, msg):
        """Switch between POSITION and VELOCITY control modes"""
        new_mode = msg.data.upper()
        if new_mode in ["POSITION", "VELOCITY"]:
            if new_mode != self.control_mode:
                self.control_mode = new_mode
                self.get_logger().info(f"Control mode switched to: {self.control_mode}")

                if self.control_mode == "VELOCITY":
                    # Initialize velocity mode with current position
                    self.setpoint_pos[0] = self.state_pos[0]
                    self.setpoint_pos[1] = self.state_pos[1]
                    self.velocity_enabled = True
                    self.last_position_update = self.get_clock().now()
                    self.get_logger().info(
                        f"Velocity mode initialized at position: [{self.setpoint_pos[0]:.3f}, {self.setpoint_pos[1]:.3f}]"
                    )
                else:
                    self.velocity_enabled = False
        else:
            self.get_logger().warning(
                f"Invalid control mode: {new_mode}. Use POSITION or VELOCITY"
            )

    def velocity_setpoint_callback(self, msg):
        """Set velocity setpoints for velocity control mode"""
        self.velocity_setpoint[0] = msg.x  # vx
        self.velocity_setpoint[1] = msg.y  # vy
        #add sensor value and pid with setpoint to get new velocity setpoint
        if self.control_mode != "VELOCITY":
            self.get_logger().warning(
                "Received velocity setpoint but not in VELOCITY mode"
            )
        else:
            self.get_logger().info(f"Velocity setpoint: vx={msg.x:.3f}, vy={msg.y:.3f}")

    def goal_callback(self, msg):
        """Position goal callback - only active in POSITION mode"""
        if self.control_mode == "POSITION":
            self.setpoint_pos[0] = msg.pose.position.x
            self.setpoint_pos[1] = msg.pose.position.y
            self.setpoint_hover[6] = msg.pose.position.z
            self.get_logger().info(
                f"NEW GOAL (POSITION): X={msg.pose.position.x:.2f}, Y={msg.pose.position.y:.2f}, Z={msg.pose.position.z:.2f}"
            )
        else:
            self.get_logger().warning(
                "Received position goal but in VELOCITY mode - ignored"
            )

    def setpoint_callback(self, msg):
        """Setpoint callback - behavior depends on control mode"""
        # Attitude setpoints always apply
        self.setpoint_hover[0] = msg.angular.x
        self.setpoint_hover[1] = msg.angular.y
        self.setpoint_hover[2] = msg.angular.z
        self.setpoint_hover[6] = msg.linear.z

        # Position setpoints only in POSITION mode
        if self.control_mode == "POSITION":
            self.setpoint_pos[0] = msg.linear.x
            self.setpoint_pos[1] = msg.linear.y

    def odom_callback(self, msg):
        pos = msg.pose.pose.position
        vel = msg.twist.twist.linear
        ang_vel = msg.twist.twist.angular
        quat = msg.pose.pose.orientation
        roll, pitch, yaw = self.euler_from_quaternion(quat.x, quat.y, quat.z, quat.w)

        self.state_pos = np.array([pos.x, pos.y, vel.x, vel.y, 0, 0])
        self.state_hover = np.array(
            [roll, pitch, yaw, ang_vel.x, ang_vel.y, ang_vel.z, pos.z, vel.z, 0]
        )

    def update_velocity_control(self):
        """Update position setpoints based on velocity setpoints"""
        if not self.velocity_enabled or self.control_mode != "VELOCITY":
            return
        # Calculate time since last update
        current_time = self.get_clock().now()
        dt_velocity = (current_time - self.last_position_update).nanoseconds / 1e9
        self.last_position_update = current_time

        # Integrate velocity to get position increments
        # This creates a continuously moving position target
        dx = self.velocity_setpoint[0] * dt_velocity
        dy = self.velocity_setpoint[1] * dt_velocity

        # Update position setpoints
        self.setpoint_pos[0] += dx
        self.setpoint_pos[1] += dy

        # Optional: Add bounds to prevent runaway
        max_position = 10.0  # meters
        self.setpoint_pos[0] = max(
            -max_position, min(max_position, self.setpoint_pos[0])
        )
        self.setpoint_pos[1] = max(
            -max_position, min(max_position, self.setpoint_pos[1])
        )

    def control_loop(self):
        # Update position setpoints if in velocity mode
        if self.control_mode == "VELOCITY":
            self.update_velocity_control()

        # POSITION CONTROL (works for both modes)
        pos_err = self.state_pos - self.setpoint_pos
        pos_error_magnitude = np.sqrt(pos_err[0] ** 2 + pos_err[1] ** 2)

        # Always apply control (no deadband)
        u_pos = -np.dot(self.K_pos, pos_err)
        commanded_pitch = u_pos[0]  # X error â†’ Pitch
        commanded_roll = u_pos[1]  # Y error â†’ Roll (negative for Y+ = LEFT)

        # Very conservative limits
        max_tilt = 0.15 # ~3 degrees
        commanded_pitch = max(-max_tilt, min(max_tilt, commanded_pitch))
        commanded_roll = max(-max_tilt, min(max_tilt, commanded_roll))

        # Always apply position control commands
        self.setpoint_hover[1] = commanded_pitch  # Pitch
        self.setpoint_hover[0] = commanded_roll  # Roll

        # Attitude control
        hover_err = self.state_hover - self.setpoint_hover
        self.z_integral += (self.setpoint_hover[6] - self.state_hover[6]) * self.dt
        self.z_integral = max(-1.0, min(1.0, self.z_integral))
        hover_err[8] = self.z_integral

        u_hover = -np.dot(self.K_hover, hover_err)

        # Output
        cmd_fin1, cmd_fin2 = u_hover[0], u_hover[1]
        cmd_fin3, cmd_fin4 = u_hover[2], u_hover[3]
        raw_thrust = u_hover[4] + self.mass * 9.81  # Compensate for weight

        fin_limit = 0.15  # Conservative
        self.publish_fin(self.pub_fin1, cmd_fin1, fin_limit)
        self.publish_fin(self.pub_fin2, cmd_fin2, fin_limit)
        self.publish_fin(self.pub_fin3, cmd_fin3, fin_limit)
        self.publish_fin(self.pub_fin4, cmd_fin4, fin_limit)

        final_thrust = max(0.0, min(120.0, float(raw_thrust)))
        t_msg = Float64()
        t_msg.data = final_thrust
        self.pub_thrust.publish(t_msg)

        # Publish status
        self.publish_status()

        # Continuous status (every 1 second)
        if self.get_clock().now().nanoseconds % 1000000000 < 10000000:
            # Determine what direction we need to move
            direction_analysis = ""
            if abs(pos_err[0]) > 0.02:  # 2cm threshold
                direction_analysis += f"X:{'+' if pos_err[0] > 0 else '-'} "
            if abs(pos_err[1]) > 0.02:
                # Y+ = LEFT in our coordinate system
                direction_analysis += f"Y:{'LEFT' if pos_err[1] > 0 else 'RIGHT'} "

            if not direction_analysis:
                direction_analysis = "ON_TARGET"

            mode_info = ""
            if self.control_mode == "VELOCITY":
                mode_info = f"VelSP:[{self.velocity_setpoint[0]:.2f},{self.velocity_setpoint[1]:.2f}] | "

            self.get_logger().info(
                f"\nMode: {self.control_mode} | {mode_info}\n"
                f"State_pos: [{self.state_pos[0]:.3f}, {self.state_pos[1]:.3f}] | \n"
                f"Setpoint_pos: [{self.setpoint_pos[0]:.3f}, {self.setpoint_pos[1]:.3f}] | \n"
                f"Err: [{pos_err[0]:.3f}, {pos_err[1]:.3f}] | \n"
                f"Mag: {pos_error_magnitude:.3f} | \n"
                f"Need: {direction_analysis} | \n"
                f"Cmd: [P={commanded_pitch:.3f}, R={commanded_roll:.3f}] \n"
                f"Velocity: [{self.state_pos[2]:.3f}, {self.state_pos[3]:.3f}] \n"
            )

    def publish_status(self):
        """Publish control system status"""
        status_msg = String()
        status_data = {
            "mode": self.control_mode,
            "pos_error": [
                float(self.state_pos[0] - self.setpoint_pos[0]),
                float(self.state_pos[1] - self.setpoint_pos[1]),
            ],
            "velocity": [float(self.state_pos[2]), float(self.state_pos[3])],
            "setpoint_pos": [float(self.setpoint_pos[0]), float(self.setpoint_pos[1])],
        }

        if self.control_mode == "VELOCITY":
            status_data["velocity_setpoint"] = [
                float(self.velocity_setpoint[0]),
                float(self.velocity_setpoint[1]),
            ]

        status_msg.data = str(status_data)
        self.pub_status.publish(status_msg)

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
    node = MinimalLQRController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
