#!/usr/bin/env python3
"""
Origin Return Diagnostic
========================

Diagnoses why drone can't return to (0,0) by analyzing:
- Position errors near origin
- Control commands being generated  
- Deadband behavior
- State estimation
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist, PoseStamped
import numpy as np
import math
import time

class OriginReturnDiagnostic(Node):
    def __init__(self):
        super().__init__("origin_diagnostic")
        self.frequency = 100.0
        self.dt = 1.0 / self.frequency

        # States
        self.state_hover = np.zeros(9)
        self.setpoint_hover = np.zeros(9)
        self.setpoint_hover[6] = 1.0

        self.state_pos = np.zeros(6)
        self.setpoint_pos = np.zeros(6)
        self.z_integral = 0.0

        # Position tracking
        self.position_history = []
        self.max_history = 500  # 5 seconds at 100Hz

        # Proven gains
        self.K_hover = np.array([
            [ 2.236068,  0.000000, -1.581139,  0.805974,  0.000000, -0.651983, -0.000000, -0.000000,  0.000000],
            [-2.236068,  0.000000, -1.581139, -0.805974,  0.000000, -0.651983, -0.000000,  0.000000,  0.000000],
            [ 0.000000, -2.236068, -1.581139,  0.000000, -0.805974, -0.651983,  0.000000, -0.000000, -0.000000],
            [-0.000000,  2.236068, -1.581139, -0.000000,  0.805974, -0.651983, -0.000000,  0.000000,  0.000000],
            [-0.000000, -0.000000, -0.000000, -0.000000, -0.000000, -0.000000,  1.793339,  1.751954, -0.632456]
        ])

        # Position control gains (with Y-axis corrected)
        self.K_pos = np.array([
            [+0.12,  0.0,  +0.25,  0.0,  0.0, 0.0],  # X control
            [ 0.0,  -0.12,  0.0,  -0.25, 0.0, 0.0]   # Y control (Y+ = LEFT)
        ])

        # Diagnostic parameters
        self.deadband_threshold = 0.08  # 8cm deadband
        self.min_control_threshold = 0.01  # Minimum control output to be considered active
        
        # Publishers
        self.pub_fin1 = self.create_publisher(Float64, "/drone/fin_1/position", 10)
        self.pub_fin2 = self.create_publisher(Float64, "/drone/fin_2/position", 10)
        self.pub_fin3 = self.create_publisher(Float64, "/drone/fin_3/position", 10)
        self.pub_fin4 = self.create_publisher(Float64, "/drone/fin_4/position", 10)
        self.pub_thrust = self.create_publisher(Float64, "/drone/cmd_thrust", 10)

        # Subscribers
        self.create_subscription(Odometry, "/odom", self.odom_callback, 10)
        self.create_subscription(PoseStamped, "/drone/goal", self.goal_callback, 10)

        self.create_timer(self.dt, self.control_loop)
        self.get_logger().info("ORIGIN RETURN DIAGNOSTIC - Analyzing why drone can't reach (0,0)")

    def goal_callback(self, msg):
        self.setpoint_pos[0] = msg.pose.position.x
        self.setpoint_pos[1] = msg.pose.position.y
        self.setpoint_hover[6] = msg.pose.position.z
        
        # Clear history when new goal is set
        self.position_history = []
        
        self.get_logger().info(f"NEW GOAL: X={msg.pose.position.x:.3f}, Y={msg.pose.position.y:.3f}, Z={msg.pose.position.z:.3f}")

    def odom_callback(self, msg):
        pos = msg.pose.pose.position
        vel = msg.twist.twist.linear
        ang_vel = msg.twist.twist.angular
        quat = msg.pose.pose.orientation
        roll, pitch, yaw = self.euler_from_quaternion(quat.x, quat.y, quat.z, quat.w)

        self.state_pos = np.array([pos.x, pos.y, vel.x, vel.y, 0, 0])
        self.state_hover = np.array([roll, pitch, yaw, ang_vel.x, ang_vel.y, ang_vel.z, pos.z, vel.z, 0])
        
        # Track position history
        self.position_history.append([pos.x, pos.y, time.time()])
        if len(self.position_history) > self.max_history:
            self.position_history.pop(0)

    def control_loop(self):
        # Position analysis
        pos_err = self.state_pos - self.setpoint_pos
        pos_error_magnitude = np.sqrt(pos_err[0]**2 + pos_err[1]**2)
        vel_magnitude = np.sqrt(self.state_pos[2]**2 + self.state_pos[3]**2)
        
        # Check if trying to reach origin
        target_is_origin = (abs(self.setpoint_pos[0]) < 0.01 and abs(self.setpoint_pos[1]) < 0.01)
        
        # Generate position control
        u_pos = -np.dot(self.K_pos, pos_err)
        commanded_pitch = u_pos[0]
        commanded_roll = u_pos[1]
        
        # Safety limits
        max_tilt = 0.08  # ~4.6 degrees
        commanded_pitch_limited = max(-max_tilt, min(max_tilt, commanded_pitch))
        commanded_roll_limited = max(-max_tilt, min(max_tilt, commanded_roll))
        
        # Check if control is being limited
        pitch_limited = (abs(commanded_pitch) > max_tilt)
        roll_limited = (abs(commanded_roll) > max_tilt)
        
        # Apply control (always active for diagnosis)
        self.setpoint_hover[1] = commanded_pitch_limited
        self.setpoint_hover[0] = commanded_roll_limited
        
        # Attitude control
        hover_err = self.state_hover - self.setpoint_hover
        self.z_integral += (self.setpoint_hover[6] - self.state_hover[6]) * self.dt
        self.z_integral = max(-1.0, min(1.0, self.z_integral))
        hover_err[8] = self.z_integral
        
        u_hover = -np.dot(self.K_hover, hover_err)
        
        # Output
        cmd_fin1, cmd_fin2 = u_hover[0], u_hover[1]
        cmd_fin3, cmd_fin4 = u_hover[2], u_hover[3]
        raw_thrust = u_hover[4] + 7.85
        
        fin_limit = 0.2
        self.publish_fin(self.pub_fin1, cmd_fin1, fin_limit)
        self.publish_fin(self.pub_fin2, cmd_fin2, fin_limit)
        self.publish_fin(self.pub_fin3, cmd_fin3, fin_limit)
        self.publish_fin(self.pub_fin4, cmd_fin4, fin_limit)
        
        final_thrust = max(0.0, min(15.0, float(raw_thrust)))
        t_msg = Float64()
        t_msg.data = final_thrust
        self.pub_thrust.publish(t_msg)
        
        # ENHANCED DIAGNOSTIC LOGGING
        if self.get_clock().now().nanoseconds % 500000000 < 10000000:  # Every 0.5 seconds
            
            # Analyze control authority
            control_magnitude = np.sqrt(commanded_pitch**2 + commanded_roll**2)
            control_after_limits = np.sqrt(commanded_pitch_limited**2 + commanded_roll_limited**2)
            
            # Check movement progress
            movement_analysis = self.analyze_movement_progress()
            
            # Deadband analysis
            in_deadband = pos_error_magnitude < self.deadband_threshold
            has_control_authority = control_magnitude > self.min_control_threshold
            
            # Origin-specific analysis
            if target_is_origin:
                self.get_logger().info("=" * 80)
                self.get_logger().info("ORIGIN RETURN ANALYSIS")
                self.get_logger().info(f"Current pos: [{self.state_pos[0]:.4f}, {self.state_pos[1]:.4f}]")
                self.get_logger().info(f"Position err: [{pos_err[0]:.4f}, {pos_err[1]:.4f}] (mag: {pos_error_magnitude:.4f}m)")
                self.get_logger().info(f"Velocity: [{self.state_pos[2]:.4f}, {self.state_pos[3]:.4f}] (mag: {vel_magnitude:.4f}m/s)")
                
                self.get_logger().info(f"Raw control: [P={commanded_pitch:.4f}, R={commanded_roll:.4f}] (mag: {control_magnitude:.4f})")
                self.get_logger().info(f"Limited ctrl: [P={commanded_pitch_limited:.4f}, R={commanded_roll_limited:.4f}] (mag: {control_after_limits:.4f})")
                
                if pitch_limited or roll_limited:
                    self.get_logger().warn(f"CONTROL LIMITING: Pitch={pitch_limited}, Roll={roll_limited}")
                
                if in_deadband:
                    self.get_logger().warn(f"IN DEADBAND: {pos_error_magnitude:.4f}m < {self.deadband_threshold:.4f}m threshold")
                
                if not has_control_authority:
                    self.get_logger().warn(f"INSUFFICIENT CONTROL: {control_magnitude:.4f} < {self.min_control_threshold:.4f} threshold")
                
                self.get_logger().info(f"Movement: {movement_analysis}")
                self.get_logger().info("=" * 80)
                
            else:
                # Regular status for non-origin targets
                self.get_logger().info(
                    f"Pos: [{self.state_pos[0]:.3f}, {self.state_pos[1]:.3f}] | "
                    f"Target: [{self.setpoint_pos[0]:.3f}, {self.setpoint_pos[1]:.3f}] | "
                    f"Err: {pos_error_magnitude:.3f}m | "
                    f"Ctrl: {control_magnitude:.3f}"
                )

    def analyze_movement_progress(self):
        """Analyze if drone is making progress toward target"""
        if len(self.position_history) < 50:  # Need at least 0.5 seconds of data
            return "INSUFFICIENT_HISTORY"
        
        # Compare current position to position 2 seconds ago
        current_pos = np.array([self.state_pos[0], self.state_pos[1]])
        old_pos = np.array([self.position_history[0][0], self.position_history[0][1]])
        
        # Calculate movement and direction
        movement_vector = current_pos - old_pos
        movement_distance = np.linalg.norm(movement_vector)
        
        # Calculate desired direction
        target_pos = np.array([self.setpoint_pos[0], self.setpoint_pos[1]])
        desired_vector = target_pos - current_pos
        desired_distance = np.linalg.norm(desired_vector)
        
        if movement_distance < 0.01:
            return "STATIONARY"
        
        if desired_distance < 0.01:
            return "AT_TARGET"
        
        # Check if moving toward target
        if desired_distance > 0.01 and movement_distance > 0.01:
            # Normalize vectors
            movement_unit = movement_vector / movement_distance
            desired_unit = desired_vector / desired_distance
            
            # Calculate alignment (-1 to 1, where 1 = perfect alignment)
            alignment = np.dot(movement_unit, desired_unit)
            
            if alignment > 0.5:
                return f"TOWARD_TARGET(align={alignment:.2f})"
            elif alignment < -0.5:
                return f"AWAY_FROM_TARGET(align={alignment:.2f})"
            else:
                return f"SIDEWAYS(align={alignment:.2f})"
        
        return f"MOVING({movement_distance:.3f}m)"

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
    
    print("\n=== ORIGIN RETURN DIAGNOSTIC ===")
    print("This controller will analyze why the drone can't return to (0,0)")
    print("")
    print("Test procedure:")
    print("1. Move drone away from origin:")
    print("   ros2 topic pub /drone/goal geometry_msgs/msg/PoseStamped \"pose: {position: {x: 1.0, y: 1.0, z: 1.5}}\"")
    print("2. Command return to origin:")
    print("   ros2 topic pub /drone/goal geometry_msgs/msg/PoseStamped \"pose: {position: {x: 0.0, y: 0.0, z: 1.5}}\"")
    print("3. Watch detailed diagnostic output")
    print("")
    print("The diagnostic will show:")
    print("- Exact position and errors")
    print("- Control commands being generated") 
    print("- Whether control is being limited")
    print("- Movement progress analysis")
    print("- Deadband and threshold issues")
    print("")
    
    node = OriginReturnDiagnostic()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
