# THRUST VECTORING DRONE
**ROS2 PROJECT**

02 DEC, 2025

---

## 📋 สารบัญ

1. [Overview](#-overview)
2. [System Architecture](#-system-architecture)
3. [General Information](#-general-information)
4. [Control System](#-control-system)
5. [Hardware Design](#-hardware-design)
6. [ROS2 Implementation](#-ros2-implementation)
7. [Testing & Results](#-testing--results)
8. [Installation & Setup](#-installation--setup)
9. [Usage](#-usage)

---

## 🎯 Overview

โปรเจกต์นี้พัฒนาระบบ **Thrust Vectoring Drone** โดยใช้ ROS2 เป็น framework หลักในการควบคุมและสื่อสาร ระหว่าง Ground Station (PC) และ Drone ผ่านระบบ WiFi

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      PC (AGENT)                             │
│  ┌──────────┐              ┌──────────┐                    │
│  │  RVIZ2   │              │  TELEOP  │                    │
│  └──────────┘              └──────────┘                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                    WiFi │ Communication
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   DRONE (CLIENT)                            │
│                                                             │
│  ┌──────────────────┐        ┌─────────────────┐          │
│  │ FLIGHT CONTROLLER│───────▶│    ACTUATORS    │          │
│  │                  │        │  - ESC          │          │
│  │  - Control Logic │        │  - Ducted Fan   │          │
│  │  - LQR + Kalman  │        │  - 4x Servos    │          │
│  └────────┬─────────┘        └─────────────────┘          │
│           │                                                 │
│           ▼                                                 │
│  ┌──────────────────┐        ┌─────────────────┐          │
│  │     SENSORS      │        │ POWER SYSTEM    │          │
│  │  - IMU           │        │  - Battery      │          │
│  │  - GPS           │        │  - Regulator    │          │
│  │  - TOF Sensor    │        └─────────────────┘          │
│  │  - OLED Display  │                                      │
│  └──────────────────┘                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ System Architecture

### ROS2 Node Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          PC (AGENT)                             │
│                                                                 │
│  ┌─────────────────┐              ┌──────────────────┐        │
│  │     RVIZ2       │              │     TELEOP       │        │
│  │                 │              │                  │        │
│  │ Subscribers:    │              │ Publishers:      │        │
│  │ • /robot_desc   │              │ • /cmd_vel       │        │
│  │ • /tf           │              │                  │        │
│  └─────────────────┘              └──────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                         WiFi │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DRONE (CLIENT)                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         DRONE ROBOT STATE PUBLISHER                      │  │
│  │                                                          │  │
│  │  Publishers:                                            │  │
│  │  • /tf                                                  │  │
│  │  • /robot_description                                   │  │
│  │                                                          │  │
│  │  Subscribers:                                           │  │
│  │  • /joint_states                                        │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                         │
│  ┌────────────────────▼─────────────────────────────────────┐  │
│  │              DRONE POSE NODE                            │  │
│  │                                                          │  │
│  │  Publishers:                                            │  │
│  │  • /drone/pose                                          │  │
│  │  • /drone/angle                                         │  │
│  │  • /fin/angle                                           │  │
│  │                                                          │  │
│  │  Subscribers:                                           │  │
│  │  • /cmd_vel                                             │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                         │
│  ┌────────────────────▼─────────────────────────────────────┐  │
│  │              FIN ANGLE NODE                             │  │
│  │                                                          │  │
│  │  Publishers:                                            │  │
│  │  • /joint_states                                        │  │
│  │                                                          │  │
│  │  Subscribers:                                           │  │
│  │  • /fin/angle                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### System Diagram - Data Flow

```
┌──────────┐                                      ┌──────────┐
│  RVIZ2   │◄─────────────────────────────────────│  DRONE   │
└──────────┘         Show TF of drone            └──────────┘
                                                       │
┌──────────┐                                          │
│  TELEOP  │──────────────────────────────────────►  │
└──────────┘    Publish /cmd_vel for velocity        │
                                                      │
                                                      ▼
                                        ┌─────────────────────────┐
                                        │  Speed Control → ESC    │
                                        │         ▼               │
                                        │    Ducted Fan           │
                                        │                         │
                                        │  Sensors:               │
                                        │  • IMU                  │
                                        │  • GPS                  │
                                        │  • OLED                 │
                                        │  • TOF Sensor           │
                                        └─────────────────────────┘
```

---

## 📊 General Information

### Specifications

| Parameter | Value | Unit |
|-----------|-------|------|
| **Takeoff Weight** | 707 | g |
| **Max Thrust** | 1250 | g |
| **T/W Ratio** | 1.79 | - |
| **Flight Time** | 5 | minutes |
| **Dimensions** | 100 x 100 x 160 | mm |

### Performance Characteristics

- **Thrust-to-Weight Ratio**: 1.79 (excellent maneuverability)
- **Endurance**: 5 minutes flight time
- **Compact Design**: 100mm x 100mm footprint
- **Control**: 4-fin thrust vectoring system

---

## 🎮 Control System

### LQR Controller

ระบบใช้ **Linear Quadratic Regulator (LQR)** สำหรับการควบคุมการบินที่เหมาะสมที่สุด

```
┌─────────┐    ┌──────────┐    ┌────────────────┐    ┌─────────┐
│  Target │───▶│   LQR    │───▶│ SERVO +        │───▶│ Output  │
│ Altitude│    │          │    │ THRUSTER       │    │ [4 fin  │
└─────────┘    │          │    │ CONTROLLER     │    │+ thrust]│
               └────▲─────┘    └────────────────┘    └─────────┘
                    │
               ┌────┴─────┐
               │   IMU    │
               │   TOF    │
               │ Velocity │
               └──────────┘
               
Input: roll, pitch, yaw, altitude
Output: 4 fin angles + thruster speed
```

**State Space Model:**

อ้างอิง: [Master Thesis - Emil Jacobsen](https://vbn.aau.dk/ws/files/421577367/Master_Thesis_Emil_Jacobsen_v5.pdf)

```
ẋ = Ax + Bu
y = Cx + Du

Where:
x = [x, y, z, φ, θ, ψ, ẋ, ẏ, ż, φ̇, θ̇, ψ̇]ᵀ
u = [fin1, fin2, fin3, fin4, thrust]ᵀ
```

### Kalman Filter

ใช้ **Kalman Filter** สำหรับการประมาณค่า state ที่แม่นยำ

```
┌────────────────────────────────────────┐
│         KALMAN FILTER                  │
│                                        │
│  ┌──────────────┐  ┌────────────────┐ │
│  │   PREDICT    │  │  MEASUREMENT   │ │
│  │              │  │     UPDATE     │ │
│  │ Extrapolate  │─▶│  Update state  │ │
│  │  the state   │  │with measurement│ │
│  └──────────────┘  └────────────────┘ │
└────────────────────────────────────────┘

Combined System:
┌─────────┐    ┌─────────┐    ┌──────────┐    ┌─────────┐
│  Target │───▶│ KALMAN  │───▶│   LQR    │───▶│ SERVO + │
│Altitude │    │         │    │          │    │THRUSTER │
└─────────┘    └────▲────┘    └──────────┘    └─────────┘
                    │
               ┌────┴─────┐
               │   IMU    │
               │   TOF    │
               │ Velocity │
               └──────────┘
```

**Kalman Filter Equations:**

Prediction Step:
```
x̂ₖ⁻ = Aₖ₋₁x̂ₖ₋₁ + Bₖ₋₁uₖ₋₁
Pₖ⁻ = Aₖ₋₁Pₖ₋₁Aₖ₋₁ᵀ + Qₖ₋₁
```

Update Step:
```
Kₖ = Pₖ⁻Hₖᵀ(HₖPₖ⁻Hₖᵀ + Rₖ)⁻¹
x̂ₖ = x̂ₖ⁻ + Kₖ(zₖ - Hₖx̂ₖ⁻)
Pₖ = (I - KₖHₖ)Pₖ⁻
```

---

## 🔧 Hardware Design

### Thrust Vane Mechanism

```
┌──────────────────────────────────────┐
│      THRUST VANE FORCE               │
│                                      │
│           ┌────────┐                 │
│           │ SERVO  │                 │
│           │ MOTOR  │                 │
│           └───┬────┘                 │
│               │                      │
│         ┌─────▼─────┐                │
│         │   THRUST  │                │
│         │    VANE   │                │
│         └───────────┘                │
│               │                      │
│               ▼                      │
│         Vectored Thrust              │
└──────────────────────────────────────┘
```

### Airfoil Design

โปรเจกต์มีการออกแบบ **Airfoil** สำหรับ thrust vanes เพื่อประสิทธิภาพสูงสุด

- ใช้หลักการ aerodynamics
- ออกแบบให้มีแรงต้านต่ำ
- ประสิทธิภาพสูงในการเปลี่ยนทิศทางแรงขับ

---

## 🚀 ROS2 Implementation

### ROS2 Nodes

#### 1. Drone Robot State Publisher
```python
# Publishers
/tf                    # TF transformations
/robot_description     # URDF model

# Subscribers
/joint_states         # Joint positions from servos
```

#### 2. Drone Pose Node
```python
# Publishers
/drone/pose          # Current position (x, y, z)
/drone/angle         # Current attitude (roll, pitch, yaw)
/fin/angle           # Fin angles [fin1, fin2, fin3, fin4]

# Subscribers
/cmd_vel             # Velocity commands from teleop
```

#### 3. Fin Angle Node
```python
# Publishers
/joint_states        # Joint states for URDF visualization

# Subscribers
/fin/angle           # Desired fin angles from controller
```

#### 4. RVIZ2 Node
```python
# Subscribers
/robot_description   # Load drone model
/tf                  # Display drone position and orientation
```

#### 5. Teleop Node
```python
# Publishers
/cmd_vel             # Twist messages for drone velocity control
```

### System Architecture (Gazebo Simulation)

```
┌──────────────────────────────────────────────────────────┐
│              LQR CONTROLLER                              │
│                                                          │
│  Publishers:                                            │
│  • /drone/fin/position                                  │
│  • /drone/cmd_thrust                                    │
│                                                          │
│  Subscribers:                                           │
│  • /drone/control_mode                                  │
│  • /drone/setpoint                                      │
│  • /drone/velocity_setpoint                             │
│  • /odom                                                │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│              TVC CONTROLLER                              │
│                                                          │
│  Publishers:                                            │
│  • /drone/thrust                                        │
│                                                          │
│  Subscribers:                                           │
│  • /drone/fin/position                                  │
│  • /drone/cmd_thrust                                    │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│                   GAZEBO                                 │
│                                                          │
│  Publishers:                                            │
│  • /odom                                                │
│                                                          │
│  Subscribers:                                           │
│  • /drone/thrust                                        │
└──────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing & Results

### Test Configurations

#### 1. Stabilize Test
- ทดสอบความสามารถในการรักษาท่าทางบิน
- ตรวจสอบ response time ของ LQR controller
- วัดค่า overshoot และ settling time

#### 2. Position Control
- ทดสอบการควบคุมตำแหน่งแบบ closed-loop
- ตรวจสอบความแม่นยำในการเคลื่อนที่ไปยังจุดเป้าหมาย
- วัด position error และ trajectory tracking

#### 3. Velocity Control
- ทดสอบการควบคุมความเร็วในแต่ละแกน
- ตรวจสอบ response ต่อ velocity commands
- วัด acceleration และ deceleration characteristics

### Hardware Testing

#### Prototype Vectoring Drone
- สร้าง prototype เพื่อทดสอบกลไก thrust vectoring
- ทดสอบความแข็งแรงของโครงสร้าง
- วัดประสิทธิภาพของ thrust vanes

#### Station Test Drone Gimbal
- ทดสอบบนขาตั้ง (test stand) ก่อนบินจริง
- วัดแรงขับและการตอบสนองของ servos
- ทดสอบระบบควบคุมในสภาวะปลอดภัย

#### Drone Flight Test
- ทดสอบบินจริง
- ตรวจสอบความเสถียรและควบคุมได้
- บันทึก flight data สำหรับวิเคราะห์

### RVIZ2 Visualization

แสดงผล real-time:
- ตำแหน่งและทิศทางของ drone
- TF transformations
- Joint states (fin angles)
- Trajectory path

---

## 💻 Installation & Setup

### Prerequisites

**Hardware Requirements:**
- Drone hardware with flight controller
- WiFi module for communication
- Sensors: IMU, GPS, TOF, OLED
- 4x Servos + ESC + Ducted fan

**Software Requirements:**
- Ubuntu 22.04 (Jammy)
- ROS2 Humble
- Python 3.10+
- Gazebo (for simulation)

### Installation Steps

#### 1. Install ROS2 Humble

```bash
# Setup sources
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# Setup ROS2 repository
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Install ROS2 Humble
sudo apt update
sudo apt install ros-humble-desktop
```

#### 2. Install Dependencies

```bash
# ROS2 packages
sudo apt install ros-humble-gazebo-ros-pkgs
sudo apt install ros-humble-rviz2
sudo apt install ros-humble-robot-state-publisher
sudo apt install ros-humble-joint-state-publisher
sudo apt install ros-humble-teleop-twist-keyboard

# Python packages
pip install numpy scipy matplotlib
pip install pyserial
```

#### 3. Clone and Build Workspace

```bash
# Create workspace
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

# Clone repository
git clone https://github.com/yourusername/thrust_vectoring_drone.git

# Build workspace
cd ~/ros2_ws
colcon build --symlink-install

# Source workspace
source ~/ros2_ws/install/setup.bash
```

#### 4. Configure Network

**On Drone (Client):**
```bash
# Edit network config
sudo nano /etc/netplan/01-netcfg.yaml

# Add WiFi configuration
network:
  version: 2
  wifis:
    wlan0:
      dhcp4: no
      addresses: [192.168.1.100/24]
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8]

# Apply config
sudo netplan apply
```

**On PC (Agent):**
```bash
# Set ROS_DOMAIN_ID
echo "export ROS_DOMAIN_ID=0" >> ~/.bashrc

# Set RMW implementation
echo "export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp" >> ~/.bashrc

source ~/.bashrc
```

---

## 🎯 Usage

### Running the System

#### On Drone (Client)

```bash
# Terminal 1: Launch drone nodes
ros2 launch thrust_vectoring_drone drone_launch.py

# Terminal 2: Start flight controller
ros2 run thrust_vectoring_drone flight_controller_node

# Terminal 3: Monitor sensors
ros2 topic echo /drone/pose
ros2 topic echo /drone/angle
```

#### On PC (Agent)

```bash
# Terminal 1: Launch RVIZ2
ros2 launch thrust_vectoring_drone rviz_launch.py

# Terminal 2: Start teleop
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# Terminal 3: Monitor topics
ros2 topic list
ros2 topic echo /cmd_vel
```

### Control Commands

**Keyboard Teleoperation:**
```
Moving around:
   u    i    o
   j    k    l
   m    ,    .

q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%

CTRL-C to quit
```

**ROS2 Commands:**

```bash
# Set velocity
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"

# Check drone status
ros2 topic echo /drone/pose
ros2 topic echo /drone/angle

# View TF tree
ros2 run tf2_tools view_frames
```

### Gazebo Simulation

```bash
# Launch Gazebo simulation
ros2 launch thrust_vectoring_drone gazebo_launch.py

# In another terminal, run controller
ros2 run thrust_vectoring_drone lqr_controller_node

# Monitor odometry
ros2 topic echo /odom
```

### Flight Modes

#### 1. Manual Mode
```bash
ros2 service call /drone/set_mode std_srvs/srv/SetBool "{data: false}"
```

#### 2. Stabilize Mode
```bash
ros2 service call /drone/set_mode std_srvs/srv/SetBool "{data: true}"
```

#### 3. Position Hold
```bash
ros2 topic pub /drone/setpoint geometry_msgs/msg/Point "{x: 0.0, y: 0.0, z: 1.0}"
```

---

## 📸 Gallery

### RVIZ2 Visualization
![RVIZ2 Display](images/rviz2_display.png)

### Prototype Testing
![Prototype Drone](images/prototype_drone.png)

### Flight Testing
![Drone Flight](images/drone_flight.png)

### Station Test
![Test Stand](images/test_stand.png)

---

## 📚 References

1. **State Space Model & LQR Controller**
   - Master Thesis: Emil Jacobsen
   - https://vbn.aau.dk/ws/files/421577367/Master_Thesis_Emil_Jacobsen_v5.pdf

2. **ROS2 Documentation**
   - https://docs.ros.org/en/humble/

3. **Kalman Filter Implementation**
   - Welch, G., & Bishop, G. "An Introduction to the Kalman Filter"

4. **Thrust Vectoring Control**
   - Various academic papers on vectored thrust UAVs

---

## 👥 Team

**Project Members:**
- [Your Name] - Control Systems
- [Team Member 2] - Hardware Design
- [Team Member 3] - Software Development
- [Team Member 4] - Testing & Integration

**Advisor:**
- [Advisor Name]

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- ROS2 Community
- Gazebo Development Team
- Academic advisors and mentors
- All contributors to this project

---

## 📧 Contact

For questions or collaboration:
- Email: your.email@university.edu
- GitHub: https://github.com/yourusername/thrust_vectoring_drone

---

**Last Updated:** 02 December, 2025
