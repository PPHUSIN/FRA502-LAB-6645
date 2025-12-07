# TVC Drone Simulation with LQR Control

A comprehensive ROS2 simulation of a thrust vector control (TVC) drone with aerodynamic fins and advanced LQR-based control systems. This project implements a unique drone design using four aerodynamic control fins for attitude control instead of traditional rotor speed differential.

## System Overview

This simulation models a novel drone configuration where:
- **Propulsion**: Single thrust source for vertical lift
- **Control**: Four aerodynamic fins provide roll, pitch, and yaw control
- **Control System**: Dual-loop LQR controllers for attitude and position control
- **Modes**: Position and velocity control capabilities

## Architecture

### Control System Hierarchy
```
┌─────────────────────────────────────────────────────────────────────┐
│                          Position Controller                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │   Position      │    │    Velocity     │    │     Goal        │  │
│  │     Mode        │    │      Mode       │    │   Commands      │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘  │
│                                │                                     │
│                         Position Setpoints                          │
└─────────────────────────────────┼───────────────────────────────────┘
                                  │
┌─────────────────────────────────┼───────────────────────────────────┐
│                        Attitude Controller                          │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    LQR Hover Control                       │    │
│  │  [Roll, Pitch, Yaw, ω_x, ω_y, ω_z, Z, Z_dot, Z_integral] │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                │                                     │
│                           Fin Commands                              │
└─────────────────────────────────┼───────────────────────────────────┘
                                  │
┌─────────────────────────────────┼───────────────────────────────────┐
│                         TVC Aerodynamics                            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │  Fin 1  │  │  Fin 2  │  │  Fin 3  │  │  Fin 4  │  │ Thrust  │   │
│  │ (Front) │  │ (Back)  │  │ (Left)  │  │ (Right) │  │         │   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │
│                                │                                     │
│                       Forces & Torques                              │
└─────────────────────────────────┼───────────────────────────────────┘
                                  │
                              Gazebo Physics
```

## Component Details

### 1. Launch System (`simulation_launch.py`)
**Purpose**: Orchestrates the complete simulation environment

**Features**:
- Gazebo world setup with aerodynamics environment
- URDF/XACRO robot model processing
- Multi-node launch coordination
- Robot state publisher initialization

**Key Components Launched**:
- Gazebo simulation environment
- Robot state publisher
- Drone entity spawner
- TVC controller node
- LQR controller node

### 2. LQR Gain Calculation (`find_lqr.py`)
**Purpose**: Computes optimal control gains using Linear Quadratic Regulator theory

**Physical Parameters**:
```python
# Drone Configuration
MASS = 0.707 kg                    # Total drone mass
Ixx, Iyy = 0.01 kg⋅m²            # Roll/Pitch inertia
Izz = 0.02 kg⋅m²                  # Yaw inertia
L_VERT = 0.048 m                  # Vertical arm length
L_HORZ = 0.029 m                  # Horizontal arm length

# Aerodynamic Configuration
D_PROP = 0.07 m                   # Propeller diameter (7cm)
FIN_SPAN = 0.125 m                # Fin span (12.5cm)
FIN_CHORD = 0.060 m               # Fin chord (6cm)
CL_alpha = 6.18 rad⁻¹             # Lift curve slope
```

**Control Matrices**:
- **Hover Control**: 9-state system (attitude + altitude)
- **Position Control**: 6-state system (position + velocity)
- **Weighting**: Optimized for stability and response time

### 3. LQR Controller Node (`lqr_node.py`)
**Purpose**: Real-time control system implementing dual-mode operation

#### Control Modes

**Position Mode**:
- Direct position setpoint tracking
- Immediate goal following
- Traditional waypoint navigation

**Velocity Mode**:
- Continuous velocity command integration
- Moving position target generation
- Suitable for teleoperation or trajectory following

#### State Vectors

**Hover State** (9 elements):
```python
[roll, pitch, yaw, ω_x, ω_y, ω_z, z, z_dot, z_integral]
```

**Position State** (6 elements):
```python
[x, y, x_dot, y_dot, unused, unused]
```

#### ROS2 Interface

**Publishers**:
- `/drone/fin_1/position` → `/drone/fin_4/position`: Fin angle commands
- `/drone/cmd_thrust`: Thrust command
- `/drone/control_status`: System status

**Subscribers**:
- `/odom`: Vehicle odometry
- `/drone/goal`: Position goals (Position mode)
- `/drone/setpoint`: Direct setpoints
- `/drone/velocity_setpoint`: Velocity commands (Velocity mode)
- `/drone/control_mode`: Mode switching commands

### 4. TVC Aerodynamics Controller (`tvc_controller.py`)
**Purpose**: Converts fin deflections to aerodynamic forces and torques

#### Aerodynamic Model

**Momentum Theory**: Propeller-induced dynamic pressure
```python
q = 0.5 * ρ * v_exit²
where v_exit² = Thrust / (ρ * A_disk)
```

**Fin Force Generation**:
```python
Lift = q * A_fin * CL_alpha * angle
```

#### Fin-to-Control Mapping

| Fin | Position | Primary Control | Secondary Effect |
|-----|----------|----------------|------------------|
| Fin 1 | Front (X+) | Roll Control | Yaw Coupling |
| Fin 2 | Back (X-) | Roll Control | Yaw Coupling |
| Fin 3 | Left (Y+) | Pitch Control | Yaw Coupling |
| Fin 4 | Right (Y-) | Pitch Control | Yaw Coupling |

**Force/Torque Distribution**:
- **Roll Torque**: τ_x = ±F_lift × L_vert (Fins 1,2)
- **Pitch Torque**: τ_y = ±F_lift × L_vert (Fins 3,4)
- **Yaw Torque**: τ_z = -F_lift × L_horz (All fins)

## Setup and Usage

### Prerequisites
- ROS2 (Humble/Iron)
- Gazebo Classic or Ignition Gazebo
- Python 3.8+
- NumPy, SciPy

### Installation
```bash
cd ~[your-workspace]
colcon build --packages-select drone_gazebo
source install/setup.bash
```

### Running the Simulation

#### Basic Simulation Launch
```bash
ros2 launch drone_gazebo simulation_launch.py
```

#### Control Commands

**Position Mode (Default)**:
```bash
# Direct setpoint
ros2 topic pub /drone/setpoint geometry_msgs/Twist "
linear: {x: 1.0, y: 0.5, z: 1.2}
angular: {x: 0.0, y: 0.0, z: 0.0}"
```

**Switch to Velocity Mode**:
```bash
# Change control mode
ros2 topic pub /drone/control_mode std_msgs/String "data: 'VELOCITY'"

# Send velocity commands
ros2 topic pub /drone/velocity_setpoint geometry_msgs/Vector3 "
x: 0.5  # Forward velocity (m/s)
y: 0.2  # Left velocity (m/s)
z: 0.0"
```

### Monitoring System Status
```bash
# Control system status
ros2 topic echo /drone/control_status

# Vehicle odometry
ros2 topic echo /odom

# Fin positions
ros2 topic echo /drone/fin_1/position
```

## Technical Specifications

### Performance Characteristics
- **Control Frequency**: 100 Hz
- **Maximum Tilt Angle**: ±8.6° (±0.15 rad)
- **Fin Deflection Limit**: ±8.6° (±0.15 rad)
- **Thrust Range**: 0-120 N
- **Position Accuracy**: ~2cm steady-state
- **Response Time**: <0.5s for attitude, <2s for position

### Stability Margins
- **Roll/Pitch Bandwidth**: ~10 Hz
- **Yaw Bandwidth**: ~3 Hz
- **Position Loop**: ~1 Hz
- **Stability Margin**: 60° phase margin, 10dB gain margin

### Control Authority
- **Roll Control Power**: 0.013 Nm/rad
- **Pitch Control Power**: 0.013 Nm/rad  
- **Yaw Control Power**: 0.008 Nm/rad
- **Maximum Roll/Pitch Rate**: ~50°/s
- **Maximum Yaw Rate**: ~30°/s

## Gain Tuning Guidelines

### LQR Weight Matrix Tuning

**Hover Control Weights** (`Q_hov`):
```python
Q_hov = np.diag([200., 200., 20., 10., 10., 10., 3., 2., 1.])
#               [roll pitch yaw  ωx   ωy   ωz   z  z_dot z_int]
```

**Position Control Weights** (`Q_pos`):
```python
Q_pos = np.diag([1.0, 1.0, 1.8, 1.8])
#               [x    y    x_dot y_dot]
```

**Control Effort Weights** (`R`):
```python
R_hov = np.diag([1., 1., 1., 1., 0.8])  # [fin1, fin2, fin3, fin4, thrust]
R_pos = np.eye(2) * 1.0                 # [roll_cmd, pitch_cmd]
```

### Tuning Strategy
1. **Increase Position Weights**: Faster position response, potential overshoot
2. **Increase Attitude Weights**: Stiffer attitude control, better disturbance rejection
3. **Increase Control Weights**: Smoother control, slower response
4. **Decrease Integral Weight**: Faster altitude response, potential steady-state error

## Troubleshooting

### Common Issues

**Oscillations in Attitude**:
- Check fin deflection limits (reduce if needed)
- Verify aerodynamic parameters
- Reduce attitude control weights

**Poor Position Tracking**:
- Verify coordinate frame alignment
- Check position control gains
- Monitor velocity feedback

**Simulation Instability**:
- Reduce control frequency if needed
- Check URDF inertial properties
- Verify Gazebo physics timestep

### Debug Topics
```bash
# Monitor fin commands
ros2 topic echo /drone/fin_1/position

# Check thrust commands  
ros2 topic echo /drone/cmd_thrust

# View applied forces/torques
ros2 topic echo /drone/thrust

# System diagnostics
ros2 topic echo /drone/control_status
```

## License

This project is part of ongoing robotics research at King Mongkut's University of Technology Thonburi (KMUTT).

## Citation

If you use this simulation in your research, please cite:
```
@misc{tvc_drone_sim_2024,
  title={TVC Drone Simulation with LQR Control},
  author={Pao},
  institution={King Mongkut's University of Technology Thonburi},
  year={2024},
  note={Robotics and Control Systems Research}
}
```

---

**Contact**: For technical questions or collaboration opportunities, please reach out through academic channels.
