#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Wrench
from std_msgs.msg import Float64
import math


class TVCAeroController(Node):
    def __init__(self):
        super().__init__("tvc_controller")

        # --- 1. PHYSICAL DIMENSIONS (URDF) ---
        self.l_vert = 0.048  # Vertical Arm (Z)
        self.l_horz = 0.029  # Horizontal Arm (X/Y)

        # --- 2. AERODYNAMIC PARAMETERS ---
        self.rho = 1.225
        self.A_disk = math.pi * (0.07 / 2) ** 2
        self.A_fin = 0.0028
        self.CL_alpha = 6.18  # Lift Curve Slope (per radian)

        # --- STATE ---
        self.current_thrust = 0.0
        self.fin_angles = {"fin_1": 0.0, "fin_2": 0.0, "fin_3": 0.0, "fin_4": 0.0}

        # --- ROS SETUP ---
        self.wrench_pub = self.create_publisher(Wrench, "/drone/thrust", 10)
        self.create_subscription(Float64, "/drone/cmd_thrust", self.thrust_cb, 10)
        self.create_subscription(
            Float64, "/drone/fin_1/position", lambda m: self.fin_cb(m, "fin_1"), 10
        )
        self.create_subscription(
            Float64, "/drone/fin_2/position", lambda m: self.fin_cb(m, "fin_2"), 10
        )
        self.create_subscription(
            Float64, "/drone/fin_3/position", lambda m: self.fin_cb(m, "fin_3"), 10
        )
        self.create_subscription(
            Float64, "/drone/fin_4/position", lambda m: self.fin_cb(m, "fin_4"), 10
        )

        self.create_timer(0.01, self.update_physics)

    def thrust_cb(self, msg):
        self.current_thrust = max(0.0, msg.data)

    def fin_cb(self, msg, fin_name):
        self.fin_angles[fin_name] = msg.data

    def update_physics(self):
        # 1. Aerodynamics (Momentum Theory)
        if self.current_thrust > 0.01:
            v_exit_sq = self.current_thrust / (self.rho * self.A_disk)
            q = 0.5 * self.rho * v_exit_sq
        else:
            q = 0.0

        # Forces
        total_fx = 0.0
        total_fy = 0.0
        total_fz = self.current_thrust
        total_tx = 0.0
        total_ty = 0.0
        total_tz = 0.0

        for fin, angle in self.fin_angles.items():
            # Lift Force = q * A * CL * alpha
            lift = q * self.A_fin * self.CL_alpha * angle

            # --- CORRECTED MAPPING ---
            if fin == "fin_1":  # FRONT (X+) -> Deflects Y -> Controls ROLL
                total_fy += lift
                total_tx += lift * self.l_vert  # Torque around X (Roll)
                total_tz -= lift * self.l_horz  # Yaw contribution

            elif fin == "fin_2":  # BACK (X-) -> Deflects Y -> Controls ROLL
                total_fy += lift
                total_tx -= lift * self.l_vert  # Torque around X (Roll)
                total_tz -= lift * self.l_horz

            elif fin == "fin_3":  # LEFT (Y+) -> Deflects X -> Controls PITCH
                total_fx += lift
                total_ty -= lift * self.l_vert  # Torque around Y (Pitch)
                total_tz -= lift * self.l_horz

            elif fin == "fin_4":  # RIGHT (Y-) -> Deflects X -> Controls PITCH
                total_fx += lift
                total_ty += lift * self.l_vert  # Torque around Y (Pitch)
                total_tz -= lift * self.l_horz

        # Publish
        msg = Wrench()
        msg.force.x = total_fx
        msg.force.y = total_fy
        msg.force.z = total_fz
        msg.torque.x = total_tx
        msg.torque.y = total_ty
        msg.torque.z = total_tz
        self.wrench_pub.publish(msg)


def main(args=None):
    rclpy.init()
    node = TVCAeroController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
