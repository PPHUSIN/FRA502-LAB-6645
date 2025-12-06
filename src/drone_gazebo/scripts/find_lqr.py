import numpy as np
import scipy.linalg
import math

# ==========================================
# 1. PHYSICAL CONFIGURATION (EDIT THIS SECTION)
# ==========================================
M_BODY = 0.707
M_FINS = 0.0 # Add if significant
MASS = M_BODY + M_FINS

# Inertia (Keep your values)
Ixx = 0.01
Iyy = 0.01
Izz = 0.02

# Geometry (Your values)
L_VERT = 0.048
L_HORZ = 0.029

# --- AERODYNAMICS CONFIGURATION ---
# 1. PROPELLER
# Change to 0.254 for 10-inch, 0.203 for 8-inch, 0.127 for 5-inch
D_PROP = 0.07  # <--- NOTE: This value (7 cm) is more reasonable for a small drone propeller

# 2. FIN DIMENSIONS (Rectangular assumption)
# Recommended High-Auth Fin: 125mm x 60mm
FIN_SPAN  = 0.125  # Meters (Length sticking out)
FIN_CHORD = 0.060  # Meters (Width)
A_FIN = 0.0028

# 3. FIN PERFORMANCE (The "CL Constant")
# Fixed value per user request
CL_alpha = 6.18  # Lift Slope (per radian)

# ==========================================
# 2. CALCULATIONS
# ==========================================
g = 9.81
rho = 1.225
A_DISK = math.pi * (D_PROP / 2)**2

# Hover Equilibrium
T_hover = MASS * g
v_exit_sq = T_hover / (rho * A_DISK)
q_hover = 0.5 * rho * v_exit_sq

K_LIFT = q_hover * A_FIN * CL_alpha 
K_TORQUE_RP = K_LIFT * L_VERT
K_TORQUE_YAW = K_LIFT * L_HORZ 

print(f"\n--- SYSTEM ANALYSIS ---")
print(f"Prop Diameter: {D_PROP*100:.1f} cm ({D_PROP/0.0254:.1f} inch)")
print(f"Fin Area:      {A_FIN*10000:.1f} cm2 ({FIN_SPAN*1000:.0f}x{FIN_CHORD*1000:.0f}mm)")
print(f"Lift Slope:    {CL_alpha:.2f} / rad")
print(f"Control Power: {K_TORQUE_RP:.3f} Nm/rad (Roll/Pitch)")
print("-" * 30)

# ==========================================
# 3. LQR SOLVER
# ==========================================
def dlqr(A, B, Q, R):
    P = scipy.linalg.solve_discrete_are(A, B, Q, R)
    inv_term = scipy.linalg.inv(R + B.T @ P @ B)
    K = inv_term @ (B.T @ P @ A)
    return K

# Setup Matrices
nx_hov = 9
nu_hov = 5
dt = 0.01

A_hov = np.zeros((nx_hov, nx_hov))
B_hov = np.zeros((nx_hov, nu_hov))

A_hov[0,3]=1; A_hov[1,4]=1; A_hov[2,5]=1; A_hov[6,7]=1; A_hov[8,6]=-1

# Fin 1 (+Roll, -Yaw)
B_hov[3,0] = (+K_TORQUE_RP)/Ixx
B_hov[5,0] = (-K_TORQUE_YAW)/Izz
# Fin 2 (-Roll, -Yaw)
B_hov[3,1] = (-K_TORQUE_RP)/Ixx
B_hov[5,1] = (-K_TORQUE_YAW)/Izz
# Fin 3 (-Pitch, -Yaw)
B_hov[4,2] = (-K_TORQUE_RP)/Iyy
B_hov[5,2] = (-K_TORQUE_YAW)/Izz
# Fin 4 (+Pitch, -Yaw)
B_hov[4,3] = (+K_TORQUE_RP)/Iyy
B_hov[5,3] = (-K_TORQUE_YAW)/Izz

B_hov[7,4] = 1.0/MASS

Ad_hov = np.eye(nx_hov) + A_hov * dt
Bd_hov = B_hov * dt

Q_hov = np.diag([200., 200., 20., 10., 10., 10., 3., 2., 1.])
R_hov = np.diag([1., 1., 1., 1., 0.8])

K_hover = dlqr(Ad_hov, Bd_hov, Q_hov, R_hov)

# Position Loop
nx_pos = 4
nu_pos = 2
A_pos = np.zeros((4,4)); A_pos[0,2]=1; A_pos[1,3]=1
B_pos = np.zeros((4,2)); B_pos[2,0]=g; B_pos[3,1]=-g
Ad_pos = np.eye(4) + A_pos*dt
Bd_pos = B_pos*dt
Q_pos = np.diag([1.0, 1.0, 1.8, 1.8])
R_pos = np.eye(2)*1.0
K_pos_active = dlqr(Ad_pos, Bd_pos, Q_pos, R_pos)
K_pos = np.zeros((2,6))
K_pos[:,0:4] = K_pos_active

def print_k(name, k):
    print(f"{name} = np.array([")
    for row in k:
        print("    [" + ", ".join(f"{x: .6f}" for x in row) + "],")
    print("])")

print("\n--- COPY THESE GAINS INTO lqr_node.py ---")
print_k("self.K_hover", K_hover)
print("")
print_k("self.K_pos", K_pos)