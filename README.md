# THRUST VECTORING DRONE
**FIBO FRA501 – RoboticsDev Final Project 2025**

**Institute of Field Robotics, King Mongkut's University of Technology Thonburi**

06 DEC, 2025

---

## 📋 สารบัญ

1. [Overview](#-overview)
2. [Project Objectives](#-project-objectives)
3. [Project Scope & Constraints](#-project-scope--constraints)
4. [System Architecture](#-system-architecture)
5. [General Information](#-general-information)
6. [Control System](#-control-system)
7. [Hardware Design](#-hardware-design)
8. [ROS2 & MicroROS Implementation](#-ros2--microros-implementation)
9. [Expected Results](#-expected-results)
10. [Project Timeline](#-project-timeline)
11. [Installation & Setup](#-installation--setup)
12. [Usage](#-usage)

---

## 🎯 Overview

โครงงานนี้มีวัตถุประสงค์เพื่อพัฒนา **Thrust Vectoring Drone** (โดรนแบบควบคุมทิศทางแรงขับ) ซึ่งสามารถควบคุมทิศทางของแรงขับเพื่อการทรงตัวและเคลื่อนที่ได้อย่างอิสระ โดยใช้ระบบ **ROS2** ร่วมกับ **MicroROS** เพื่อเชื่อมต่อการสื่อสารระหว่างคอมพิวเตอร์และไมโครคอนโทรลเลอร์ในแบบเรียลไทม์

ระบบถูกออกแบบให้ฝั่งคอมพิวเตอร์ทำหน้าที่ส่งคำสั่งควบคุม (การขึ้นบิน, การเปลี่ยนทิศทาง, หรือการหยุดการทำงาน) ผ่าน Topic ส่วนฝั่งไมโครคอนโทรลเลอร์จะทำหน้าที่ประมวลผลทั้งหมด ได้แก่ การอ่านค่าจากเซนเซอร์ IMU, การคำนวณท่าทาง, และการควบคุมทิศทางของแรงขับด้วย PID Controller

**คำสำคัญ:** ROS2, MicroROS, Monorotor Drone, PID Controller, Real-Time Communication

---

## 🎯 Project Objectives

1. **เพื่อพัฒนาโดรนใบพัดเดียวที่ควบคุมด้วย Thrust Vectoring ได้อย่างเสถียร**
   - ใช้การปรับมุมเอียงของมอเตอร์เพื่อควบคุมทิศทางแรงขับแทนการเพิ่มจำนวนใบพัด
   - ช่วยลดน้ำหนักและความซับซ้อนของโครงสร้างโดรน

2. **เพื่อเชื่อมต่อระบบ ROS2 และ MicroROS สำหรับการสื่อสารและสั่งงานแบบเรียลไทม์ผ่าน Wi-Fi**
   - การสื่อสารผ่านอินเทอร์เน็ตโดยใช้ MicroROS Agent
   - ระบบทำงานแบบเรียลไทม์

3. **เพื่อศึกษาความสามารถในการทรงตัว การตอบสนองต่อคำสั่ง และความเป็นไปได้ในการต่อยอดสู่การควบคุมแบบอัตโนมัติในอนาคต**

---

## 📋 Project Scope & Constraints

### ขอบเขตโครงการ

1. ใช้ **ROS2** สำหรับส่งคำสั่งควบคุมการบิน
2. ใช้ไมโครคอนโทรลเลอร์ **ESP32** ที่รัน **MicroROS** ในการควบคุม PID และการรักษาสมดุล
3. ระบบสื่อสารผ่าน **Wi-Fi Network / Local Network** โดยไม่ใช้ UART
4. ใช้ **IMU** ในการวัด pitch, roll, yaw ของโดรน
5. ใช้มอเตอร์ที่ปรับมุมเอียงได้ เพื่อสร้างการควบคุมแบบ **Thrust Vectoring**
6. แสดงผลและตรวจสอบสถานะโดรนผ่าน **Rviz**

### ข้อจำกัดการใช้งาน

- **ความสูงการบิน:** ไม่เกิน 4 เมตร
- **ระยะเวลาการบิน:** ไม่เกิน 5 นาที
- **พื้นที่ทดสอบ:** ในห้องปฏิบัติการหรือพื้นที่ปลอดภัย


### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    PC (ROS2 AGENT)                         │
│  ┌──────────┐              ┌──────────┐                    │
│  │  RVIZ2   │              │  TELEOP  │                    │
│  │          │              │          │                    │
│  │ • Monitor│              │ • Send   │                    │
│  │ • Display│              │   Commands│                   │
│  └──────────┘              └──────────┘                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                    UDP  │ Wi-Fi Communication
                         │ (MicroROS Agent)
                         │
┌────────────────────────▼────────────────────────────────────┐
│              ESP32 + MicroROS FIRMWARE                     │
│                    (DRONE CLIENT)                          │
│                                                             │
│  ┌──────────────────┐        ┌─────────────────┐          │
│  │ COMMAND RECEIVE  │───────▶│    ACTUATORS    │          │
│  │                  │        │  • ESC          │          │
│  │ • Topic Subscribe│        │  • Ducted Fan   │          │
│  │ • Wi-Fi Handler  │        │  • 4x Servos    │          │
│  └────────┬─────────┘        └─────────────────┘          │
│           │                                                 │
│           ▼                                                 │
│  ┌──────────────────┐        ┌─────────────────┐          │
│  │ PID CONTROLLER   │        │    SENSORS      │          │
│  │                  │        │  • IMU          │          │
│  │ • Attitude Ctrl  │◄───────│  • TOF Sensor   │          │
│  │ • Position Ctrl  │        │  • Data Fusion  │          │
│  │ • Thrust Vector  │        └─────────────────┘          │
│  └──────────────────┘                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ System Architecture

### Communication Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          PC (AGENT)                             │
│                                                                 │
│  ┌─────────────────┐              ┌──────────────────┐        │
│  │     RVIZ2       │              │     TELEOP       │        │
│  │                 │              │                  │        │
│  │ Subscribers:    │              │ Publishers:      │        │
│  │ • /robot_desc   │              │ • /cmd_vel       │        │
│  │ • /tf           │              │ • /drone/setpoint│        │
│  │ • /drone/pose   │              │                  │        │
│  └─────────────────┘              └──────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                         UDP  │ Wi-Fi (MicroROS Agent)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ESP32 + MicroROS (CLIENT)                   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              MicroROS NODE                               │  │
│  │                                                          │  │
│  │  Publishers:                                            │  │
│  │  • /drone/pose        (geometry_msgs/Pose)             │  │
│  │  • /drone/imu         (sensor_msgs/Imu)                │  │
│  │  • /drone/status      (diagnostic_msgs/Status)         │  │
│  │                                                          │  │
│  │  Subscribers:                                           │  │
│  │  • /cmd_vel           (geometry_msgs/Twist)            │  │
│  │  • /drone/setpoint    (geometry_msgs/Point)            │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                         │
│  ┌────────────────────▼─────────────────────────────────────┐  │
│  │              FLIGHT CONTROLLER                          │  │
│  │                                                          │  │
│  │  • IMU Data Processing                                  │  │
│  │  • PID Controller (Roll, Pitch, Yaw, Altitude)         │  │
│  │  • Thrust Vectoring Logic                               │  │
│  │  • Servo Control (4x Fins)                              │  │
│  │  • ESC Control (Thrust)                                 │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                         │
│  ┌────────────────────▼─────────────────────────────────────┐  │
│  │              HARDWARE INTERFACE                         │  │
│  │                                                          │  │
│  │  • 4x Servo Motors (Fin Control)                        │  │
│  │  • 1x ESC + Brushless Motor                             │  │
│  │  • IMU Sensor (MPU6050/BMI088)                          │  │
│  │  • TOF Distance Sensor                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### System Diagram - Data Flow

```
┌──────────┐                                      ┌──────────┐
│  RVIZ2   │◄─────────────────────────────────────│ ESP32    │
└──────────┘    Show TF, Pose, Status             │ +MicroROS│
                                                   └──────────┘
┌──────────┐                                          │
│  TELEOP  │──────────────────────────────────────►  │
└──────────┘    Publish /cmd_vel & setpoints         │
                                                      │
                                                      ▼
                                        ┌─────────────────────────┐
                                        │ PID Controller + Sensors│
                                        │         ▼               │
                                        │  • 4x Servo Control     │
                                        │  • ESC/Motor Control    │
                                        │  • IMU Data Processing  │
                                        │  • TOF Altitude         │
                                        │  • Thrust Vectoring     │
                                        └─────────────────────────┘
```

---

## 📊 General Information

### Project Specifications

| Parameter | Value | Unit | Notes |
|-----------|-------|------|-------|
| **Platform** | ESP32 + MicroROS | - | Embedded flight controller |
| **Communication** | Wi-Fi/UDP | - | Real-time MicroROS Agent |
| **Flight Altitude** | ≤ 4 | meters | Safety constraint |
| **Flight Duration** | ≤ 5 | minutes | Battery limitation |
| **Control Type** | Thrust Vectoring | - | Single propeller + 4 fins |
| **Sensors** | IMU + TOF | - | Attitude + altitude sensing |

### Performance Targets

| Parameter | Target Accuracy | Unit | Description |
|-----------|----------------|------|-------------|
| **Attitude Control** | ±10 | degrees | Roll, Pitch, Yaw precision |
| **Altitude Control** | ±5 | cm | Height maintenance accuracy |
| **Communication** | Low latency | ms | ROS2 ↔ MicroROS stability |
| **Disturbance Rejection** | Small | - | PID stability under wind |

### Technical Requirements

- **Microcontroller**: ESP32 running MicroROS firmware
- **Communication**: Wi-Fi Network / Local Network (no UART)
- **Sensors**: IMU for pitch/roll/yaw measurement
- **Actuators**: Adjustable angle motors for thrust vectoring
- **Monitoring**: Real-time status display through Rviz
- **Safety**: Flight testing in controlled laboratory environment

---

## 🎮 Control System

### PID Controller Architecture

ระบบใช้ **PID Controller** สำหรับการควบคุมการบินที่เสถียรและแม่นยำ โดย ESP32 ทำหน้าที่ประมวลผล PID แบบเรียลไทม์

```
┌─────────┐    ┌──────────┐    ┌────────────────┐    ┌─────────┐
│ Target  │───▶│   PID    │───▶│ SERVO +        │───▶│ Output  │
│Setpoint │    │Controller│    │ THRUSTER       │    │ [4 fins │
│(ROS2)   │    │(ESP32)   │    │ CONTROLLER     │    │+ thrust]│
└─────────┘    │          │    │                │    │         │
               └────▲─────┘    └────────────────┘    └─────────┘
                    │
               ┌────┴─────┐
               │   IMU    │
               │   TOF    │
               │ Feedback │
               └──────────┘
               
Input: roll, pitch, yaw, altitude setpoints (via ROS2)
Output: 4 fin angles + thruster speed
```

### PID Controller Implementation

**Multi-loop PID Structure:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    ESP32 PID CONTROLLER                        │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  ROLL PID   │  │ PITCH PID   │  │  YAW PID    │            │
│  │             │  │             │  │             │            │
│  │ Kp, Ki, Kd  │  │ Kp, Ki, Kd  │  │ Kp, Ki, Kd  │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                │                │                    │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐            │
│  │   FIN 1     │  │   FIN 2     │  │   FIN 3     │            │
│  │   SERVO     │  │   SERVO     │  │   SERVO     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│  ┌─────────────┐                  ┌─────────────┐            │
│  │ALTITUDE PID │                  │   FIN 4     │            │
│  │             │                  │   SERVO     │            │
│  │ Kp, Ki, Kd  │─────────────────▶│             │            │
│  └─────────────┘                  └─────────────┘            │
│         │                                                     │
│  ┌──────▼──────┐                                              │
│  │  THRUSTER   │                                              │
│  │    ESC      │                                              │
│  └─────────────┘                                              │
└─────────────────────────────────────────────────────────────────┘
```

**PID Equations:**

```
u(t) = Kp * e(t) + Ki * ∫e(t)dt + Kd * de(t)/dt

Where:
e(t) = setpoint - measurement
Kp = Proportional gain
Ki = Integral gain  
Kd = Derivative gain
```

### Thrust Vectoring Logic

**การควบคุมทิศทางแรงขับ:**

```
                    ┌─────────────────┐
                    │  THRUST VECTOR  │
                    │    CONTROL      │
                    │                 │
         Roll   ────┤                 ├──── Fin 1 Angle
         Pitch  ────┤  ESP32 + PID    ├──── Fin 2 Angle  
         Yaw    ────┤                 ├──── Fin 3 Angle
         Alt    ────┤                 ├──── Fin 4 Angle
                    │                 │
         IMU    ────┤                 ├──── Thrust Level
         TOF    ────┤                 │
                    └─────────────────┘
```

**Thrust Vectoring Principle:**
- แทนที่การใช้หลายใบพัด ใช้ 4 หูตัดแบบ servomotor ควบคุมทิศทางแรงขับ
- ลดน้ำหนักและความซับซ้อนของระบบ  
- เพิ่มประสิทธิภาพในการควบคุมท่าทาง

### Sensor Fusion & State Estimation

```
┌─────────────────────────────────────────────────────────────────┐
│                    SENSOR PROCESSING                            │
│                                                                 │
│  ┌─────────────┐              ┌─────────────┐                  │
│  │     IMU     │              │ TOF SENSOR  │                  │
│  │             │              │             │                  │
│  │ • Roll      │─────────────▶│ • Altitude  │                  │
│  │ • Pitch     │              │ • Distance  │                  │
│  │ • Yaw       │              │             │                  │
│  │ • Accel     │              └─────────────┘                  │
│  │ • Gyro      │                     │                         │
│  └─────────────┘                     │                         │
│         │                            │                         │
│         ▼                            ▼                         │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              KALMAN FILTER                              │  │
│  │                                                         │  │
│  │  • State Estimation                                     │  │
│  │  • Noise Filtering                                      │  │
│  │  • Sensor Fusion                                        │  │
│  └─────────────┬───────────────────────────────────────────┘  │
└────────────────┼──────────────────────────────────────────────┘
                 │
                 ▼
          To PID Controller
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

### ROS2 & MicroROS Integration

```
┌──────────────────────────────────────────────────────────┐
│              ESP32 + MicroROS NODE                       │
│                                                          │
│  Publishers:                                            │
│  • /drone/pose        (geometry_msgs/Pose)             │
│  • /drone/imu         (sensor_msgs/Imu)                │
│  • /drone/status      (diagnostic_msgs/Status)         │
│                                                          │
│  Subscribers:                                           │
│  • /cmd_vel           (geometry_msgs/Twist)            │
│  • /drone/setpoint    (geometry_msgs/Point)            │
└────────────────────┬─────────────────────────────────────┘
                     │
                UDP  │ Wi-Fi Communication
                     ▼
┌──────────────────────────────────────────────────────────┐
│                 PC ROS2 AGENT                           │
│                                                          │
│  Publishers:                                            │
│  • /cmd_vel           (from teleop)                     │
│  • /drone/setpoint    (position commands)               │
│                                                          │
│  Subscribers:                                           │
│  • /drone/pose        (for monitoring)                  │
│  • /drone/imu         (for RVIZ)                        │
│  • /drone/status      (system health)                   │
└──────────────────────────────────────────────────────────┘
```

---

## 🎯 Expected Results

### Performance Targets

1. **การควบคุมท่าทาง (Attitude Control)**
   - สามารถควบคุมโดรนให้ควบคุมองศาของตัวเองได้
   - **Target Error:** ≤ ±10 degrees (Roll, Pitch, Yaw)

2. **การควบคุมความสูง (Altitude Control)**  
   - ตัวโดรนสามารถรักษาตำแหน่งความสูงที่กำหนดให้ได้
   - **Target Error:** ≤ ±5 cm

3. **การทรงตัว (Hovering Capability)**
   - โดรนสามารถลอยตัวได้ด้วยการควบคุมแบบ Thrust Vectoring
   - เสถียรภาพในการลอยตัวโดยไม่มีการเซาะด้วยตนเอง

4. **ประสิทธิภาพการสื่อสาร (Communication Performance)**
   - การสื่อสาร ROS2 ↔ MicroROS มีความเสถียรและหน่วงต่ำ
   - Latency < 50ms สำหรับ critical commands

5. **ความทนทานต่อสิ่งรบกวน (Disturbance Rejection)**
   - PID สามารถรักษาสมดุลของโดรนได้ภายใต้ disturbance ขนาดเล็ก
   - การตอบสนองต่อลมเบา ๆ หรือการเปลี่ยนแปลงโหลด

6. **การแสดงผลแบบเรียลไทม์ (Real-time Visualization)**
   - แสดงทิศทางแรงขับและท่าทางของโดรนใน Rviz ได้อย่างถูกต้อง
   - การมอนิเตอร์สถานะแบบเรียลไทม์

### Success Criteria

✅ **Phase 1: System Integration**
- MicroROS communication established
- Basic sensor data acquisition
- Servo control functional

✅ **Phase 2: Control Implementation**  
- PID controllers tuned and stable
- Thrust vectoring mechanism working
- Real-time performance achieved

✅ **Phase 3: Flight Testing**
- Successful hover for 30+ seconds  
- Attitude control within error bounds
- Safe landing and recovery

---

## 📅 Project Timeline

### Development Schedule (6 Weeks)

| Week | Tasks | Deliverables | Status |
|------|-------|-------------|--------|
| **Week 1** | ออกแบบโครงสร้างและระบบของโดรน<br>• Frame design<br>• Motor & ESC selection<br>• Flight controller planning | • CAD models<br>• Component list<br>• System architecture | ✅ Complete |
| **Week 2** | ติดตั้งและตั้งค่า MicroROS บน ESP32<br>• ESP32 firmware development<br>• ROS2 setup on PC | • Working MicroROS node<br>• Basic communication test | ✅ Complete |
| **Week 3** | พัฒนา Communication Code<br>• WiFi communication<br>• Topic structure<br>• Message protocols | • Stable MicroROS ↔ ROS2 link<br>• Real-time data exchange | 🔄 In Progress |
| **Week 4** | พัฒนาระบบควบคุมการบินเบื้องต้น<br>• PID implementation<br>• Node/Topic/Service structure | • Flight control nodes<br>• Basic control algorithms | ⏳ Pending |
| **Week 5** | ทดสอบระบบและปรับจูนพารามิเตอร์<br>• Sensor integration testing<br>• PID tuning<br>• Real flight tests | • Tuned parameters<br>• Flight test results<br>• Performance validation | ⏳ Pending |
| **Week 6** | Final Integration & Documentation<br>• System optimization<br>• Documentation<br>• Project presentation | • Final demo<br>• Technical report<br>• Project presentation | ⏳ Pending |

### Current Milestone Status

🎯 **Current Focus: Week 3**
- Establishing robust WiFi communication
- Implementing MicroROS topic structure  
- Testing real-time data exchange reliability

📋 **Next Steps:**
1. Complete communication stability testing
2. Begin PID controller implementation  
3. Integrate IMU sensor processing
4. Develop servo control algorithms

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

1. **Master Thesis - Emil Jacobsen**
   - "Vectored Thrust Aided Attitude Control for a Single Rotor UAV"
   - https://vbn.aau.dk/ws/files/421577367/Master_Thesis_Emil_Jacobsen_v5.pdf

2. **Thrust Vectoring Control for Heavy UAVs**
   - Isaac, M. S. A., Ragab, A. R., Luna, M. A., Ale Eshagh Khoeini, M. M., & Campoy, P. (2023)
   - Employing a Redundant Communication

3. **Valle et al. (2024)**
   - การพัฒนาระบบควบคุมแรงขับแบบเบี่ยงทิศ (thrust vectoring) สำหรับ Heavy UAVs
   - การบูรณาการระหว่างเซนเซอร์ IMU เข้ากับระบบควบคุมแบบป้อนกลับ

4. **ROS2 Documentation**
   - https://docs.ros.org/en/humble/

5. **MicroROS Documentation**
   - https://micro.ros.org/

---

## 👥 Team

**FIBO FRA501 – RoboticsDev Final Project 2025**
**Institute of Field Robotics, King Mongkut's University of Technology Thonburi**

**Project Members:**
- **คุณานนต์ เศวตคชกุล** (66340500006) - System Architecture & Control
- **นาราชล นรากุลพัชร์** (66340500027) - Hardware Design & Integration  
- **ภูษิญ ประเสริฐสม** (66340500045) - Software Development & ROS2
- **วิชาญ วิชญานุภาพ** (66340500051) - MicroROS & ESP32 Firmware
- **ปวริศ ตั้งตระกูล** (66340500074) - Testing & Validation

**Institution:**
- Institute of Field Robotics
- King Mongkut's University of Technology Thonburi  
- 126 Pracha Uthit Rd, Bang Mot, Thung Khru, Bangkok, Thailand 10140

---

## 📝 License

This project is developed as part of FIBO FRA501 RoboticsDev coursework.
Copyright © 2025 by FIBO, KMUTT

---

## 🙏 Acknowledgments

- **ROS2 Community** for the excellent robotics framework
- **MicroROS Team** for embedded ROS2 support
- **Emil Jacobsen** for the foundational thesis on thrust vectoring control
- **FIBO Faculty** and **KMUTT** for project support and facilities
- **Valle et al.** for inspiration from thrust vectoring research

---

## 📧 Contact

**For questions or collaboration:**
- **Institution:** Institute of Field Robotics, KMUTT
- **Course:** FIBO FRA501 – RoboticsDev Final Project 2025
- **Location:** Bangkok, Thailand

**Project Repository:**
- GitHub: [Repository Link] (To be added)

---

**Project Status:** 🔄 **Week 3 - Development in Progress**  
**Last Updated:** 06 December, 2025
README (1).md
README (1).md (41 KB)
41 KB
