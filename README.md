# ระบบควบคุม Thrust Vectoring Drone

**โปรเจกต์: Thrust Vectoring Quadcopter Control System**

รหัสนักศึกษา:
- 66340500006
- 66340500027
- 66340500045
- 66340500051
- 66340500074 

โปรเจกต์นี้พัฒนาระบบควบคุม Drone แบบ Thrust Vectoring ที่สามารถปรับทิศทางแรงขับได้ด้วย Servo Motors โดยใช้ระบบควบคุมแบบ PID และ Flight Controller สำหรับการบินที่เสถียร พร้อมระบบควบคุมผ่าน Ground Control Station และการสื่อสารแบบ Wireless

---

## สารบัญ

1. [วัตถุประสงค์](#1-วัตถุประสงค์)
2. [ขอบเขตของโปรเจกต์](#2-ขอบเขตของโปรเจกต์)
3. [ทฤษฎีที่เกี่ยวข้อง](#3-ทฤษฎีที่เกี่ยวข้อง)
4. [คำอธิบายระบบ](#4-คำอธิบายระบบ)
5. [สถาปัตยกรรมระบบ](#5-สถาปัตยกรรมระบบ)
6. [แผนภาพระบบ](#6-แผนภาพระบบ)
7. [วิธีการดำเนินงาน](#7-วิธีการดำเนินงาน)
8. [การใช้งาน](#8-การใช้งาน)

---

## 1. วัตถุประสงค์

- พัฒนาระบบ Thrust Vectoring สำหรับ Quadcopter ด้วย Servo Motors
- ออกแบบระบบควบคุมการบินแบบ Multi-axis PID Control
- สร้าง Ground Control Station (GCS) สำหรับ monitoring และควบคุม drone
- ประยุกต์ใช้ IMU และ sensor fusion สำหรับการวัดทิศทางและความเร่ง
- พัฒนาระบบสื่อสารแบบ wireless real-time
- ทดสอบและปรับแต่งค่า PID parameters สำหรับการบินที่เสถียร

---

## 2. ขอบเขตของโปรเจกต์

### ขอบเขตการศึกษา

- ศึกษา Thrust Vectoring mechanism แบบ 4 motors + 4 servos
- ใช้ Flight Controller (ESP32/STM32) พร้อม IMU
- พัฒนา Ground Control Station ด้วย Python
- สื่อสารผ่าน WiFi/LoRa protocol
- ควบคุมด้วย PID Controller สำหรับ Roll, Pitch, Yaw

### ข้อจำกัดของระบบ

![ภาพของ Drone](drone_image.png)

**พารามิเตอร์ Drone:**

| พารามิเตอร์ | สัญลักษณ์ | ค่า | หน่วย |
|------------|----------|-----|-------|
| ระยะห่าง Motor | L | 200 | mm |
| น้ำหนักรวม | m | 800 | g |
| มุมเอียงสูงสุด | θ_max | ±15 | ° |
| แรงขับต่อ Motor | T_max | 400 | g |

**ขอบเขตการทำงาน:**

- Thrust Vector Angle: -15° ถึง +15° (แต่ละแกน)
- Roll/Pitch: -45° ถึง +45°
- Yaw Rate: -180°/s ถึง +180°/s
- Battery Voltage: 11.1V - 12.6V (3S LiPo)

**ข้อจำกัดของแรงควบคุม:**

- แรงขับสูงสุดถูกจำกัดโดย Brushless Motor specifications
- ความเร็วการตอบสนองของ servo: 60°/0.1s
- Update rate: 250Hz สำหรับ PID controller

**ข้อจำกัดอื่น ๆ:**

- ระบบไม่รองรับการบินในสภาพอากาศแรง (ลมเกิน 5 m/s)
- Flight time จำกัดที่ประมาณ 8-12 นาที
- ใช้งานกับ RC Controller หรือ GCS เท่านั้น
- ระยะควบคุมจำกัดที่ 500m (WiFi) หรือ 2km (LoRa)

---

## 3. ทฤษฎีที่เกี่ยวข้อง

### 3.1 Thrust Vectoring Principles

Thrust Vectoring คือการควบคุมทิศทางของแรงขับเพื่อควบคุมทิศทางการเคลื่อนที่ของยานพาหนะ

**ประเภทของ Thrust Vectoring:**

1. **2D Thrust Vectoring**: เอียงได้ 1 แกน (Pitch หรือ Yaw)
2. **3D Thrust Vectoring**: เอียงได้ 2 แกน (Pitch และ Yaw พร้อมกัน)

**สมการแรงขับ:**

```
T_x = T·sin(α)·cos(β)
T_y = T·sin(α)·sin(β)
T_z = T·cos(α)
```

โดย:
- T = แรงขับรวม
- α = มุมเอียง (tilt angle)
- β = มุมหมุน (azimuth angle)

### 3.2 Flight Dynamics

**6 Degrees of Freedom (6-DOF):**

ตำแหน่ง (Position):
- x, y, z ในระบบพิกัด

ทิศทาง (Orientation):
- Roll (φ): การหมุนรอบแกน X
- Pitch (θ): การหมุนรอบแกน Y
- Yaw (ψ): การหมุนรอบแกน Z

**Euler Angles:**

```
R = R_z(ψ) × R_y(θ) × R_x(φ)
```

**สมการการเคลื่อนที่:**

```
m·a = ΣF = T - mg - D
I·α = Στ
```

โดย:
- m = มวล
- I = moment of inertia
- T = thrust vector
- D = drag force
- τ = torque

### 3.3 PID Control Theory

PID (Proportional-Integral-Derivative) Controller ใช้สำหรับควบคุมการบิน:

**สมการ PID:**

```
u(t) = K_p·e(t) + K_i·∫e(t)dt + K_d·de(t)/dt
```

โดย:
- e(t) = error = setpoint - measured_value
- K_p = proportional gain
- K_i = integral gain
- K_d = derivative gain

**PID Implementation:**

```python
class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0
        self.previous_error = 0
    
    def update(self, error, dt):
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt
        
        output = (self.kp * error + 
                  self.ki * self.integral + 
                  self.kd * derivative)
        
        self.previous_error = error
        return output
```

### 3.4 IMU และ Sensor Fusion

**IMU (Inertial Measurement Unit) ประกอบด้วย:**

1. **Accelerometer**: วัดความเร่ง (3 แกน)
2. **Gyroscope**: วัดความเร็วเชิงมุม (3 แกน)
3. **Magnetometer**: วัดทิศทาง (compass)

**Complementary Filter:**

ใช้รวมข้อมูลจาก accelerometer และ gyroscope:

```
angle = α × (angle + gyro_rate × dt) + (1-α) × accel_angle
```

โดย α = 0.98 โดยทั่วไป

**Kalman Filter:**

ใช้สำหรับ sensor fusion ที่แม่นยำกว่า:

```python
# Prediction Step
x_pred = A @ x + B @ u
P_pred = A @ P @ A.T + Q

# Update Step
K = P_pred @ H.T @ inv(H @ P_pred @ H.T + R)
x = x_pred + K @ (z - H @ x_pred)
P = (I - K @ H) @ P_pred
```

### 3.5 Thrust Vectoring Control

**การคำนวณมุมเอียงของ Servo:**

สำหรับการควบคุม Roll:

```
servo_angle_left = baseline_angle + roll_correction
servo_angle_right = baseline_angle - roll_correction
```

สำหรับการควบคุม Pitch:

```
servo_angle_front = baseline_angle + pitch_correction
servo_angle_back = baseline_angle - pitch_correction
```

**Mixing Algorithm:**

```python
def calculate_servo_angles(roll, pitch, yaw):
    """
    คำนวณมุม servo จากคำสั่ง roll, pitch, yaw
    """
    # Normalize inputs
    roll = constrain(roll, -MAX_ANGLE, MAX_ANGLE)
    pitch = constrain(pitch, -MAX_ANGLE, MAX_ANGLE)
    
    # Calculate servo angles
    servo_fl = BASE_ANGLE + roll + pitch  # Front-left
    servo_fr = BASE_ANGLE - roll + pitch  # Front-right
    servo_bl = BASE_ANGLE + roll - pitch  # Back-left
    servo_br = BASE_ANGLE - roll - pitch  # Back-right
    
    return [servo_fl, servo_fr, servo_bl, servo_br]
```

### 3.6 Motor Control และ ESC

**PWM Signal สำหรับ ESC:**

- Minimum: 1000μs (Motor OFF)
- Maximum: 2000μs (Full Throttle)
- Typical Range: 1100-1900μs

**Throttle Mixing:**

```python
def calculate_motor_speeds(throttle, roll_pid, pitch_pid, yaw_pid):
    """
    คำนวณความเร็วของแต่ละ motor
    """
    m1 = throttle + pitch_pid + roll_pid - yaw_pid  # Front-right
    m2 = throttle + pitch_pid - roll_pid + yaw_pid  # Front-left
    m3 = throttle - pitch_pid - roll_pid - yaw_pid  # Back-left
    m4 = throttle - pitch_pid + roll_pid + yaw_pid  # Back-right
    
    return constrain_all([m1, m2, m3, m4], MIN_PWM, MAX_PWM)
```

---

## 4. คำอธิบายระบบ

### 4.1 ภาพรวมของระบบ

ระบบควบคุม Thrust Vectoring Drone ประกอบด้วยส่วนหลัก:

1. **Flight Controller (Onboard)**
   - ESP32/STM32 microcontroller
   - IMU (MPU6050/MPU9250)
   - PID control loops
   - Servo และ ESC control
   - Wireless communication

2. **Ground Control Station (GCS)**
   - Python-based GUI
   - Real-time telemetry display
   - Parameter tuning interface
   - Flight data logging

3. **Mechanical System**
   - 4x Brushless Motors
   - 4x ESCs
   - 4x Servo Motors (thrust vectoring)
   - Frame structure
   - Battery และ power distribution

4. **RC Controller (Optional)**
   - 2.4GHz transmitter/receiver
   - Manual flight control
   - Emergency override

### 4.2 พารามิเตอร์ของระบบ

**พารามิเตอร์ทางกายภาพ:**

| พารามิเตอร์ | สัญลักษณ์ | ค่า | หน่วย |
|------------|----------|-----|-------|
| Wheelbase | L | 200 | mm |
| Total Mass | m | 800 | g |
| Moment of Inertia (X) | I_x | 0.015 | kg·m² |
| Moment of Inertia (Y) | I_y | 0.015 | kg·m² |
| Moment of Inertia (Z) | I_z | 0.025 | kg·m² |
| Battery | - | 3S 2200mAh | LiPo |

**พารามิเตอร์ PID (เริ่มต้น):**

| Controller | K_p | K_i | K_d |
|-----------|-----|-----|-----|
| Roll | 1.5 | 0.05 | 0.8 |
| Pitch | 1.5 | 0.05 | 0.8 |
| Yaw | 2.0 | 0.1 | 0.5 |
| Altitude | 2.5 | 0.5 | 1.5 |

### 4.3 State Variables

**ตัวแปรสถานะการบิน:**

| State | สัญลักษณ์ | คำอธิบาย | หน่วย |
|-------|----------|---------|-------|
| Roll Angle | φ | มุมการหมุนรอบแกน X | rad |
| Pitch Angle | θ | มุมการหมุนรอบแกน Y | rad |
| Yaw Angle | ψ | มุมการหมุนรอบแกน Z | rad |
| Roll Rate | p | ความเร็วเชิงมุมรอบแกน X | rad/s |
| Pitch Rate | q | ความเร็วเชิงมุมรอบแกน Y | rad/s |
| Yaw Rate | r | ความเร็วเชิงมุมรอบแกน Z | rad/s |
| Altitude | z | ความสูงจากพื้น | m |
| Battery Voltage | V_bat | แรงดันแบตเตอรี่ | V |

### 4.4 Coordinate Systems

**ระบบพิกัด:**

- **Inertial Frame (NED)**: North-East-Down (ติดกับพื้นดิน)
- **Body Frame**: ติดกับตัว drone
  - X-axis: ชี้ไปข้างหน้า
  - Y-axis: ชี้ไปทางขวา
  - Z-axis: ชี้ลงด้านล่าง

**การแปลงพิกัด:**

```
v_body = R(φ,θ,ψ) × v_inertial
```

---

## 5. สถาปัตยกรรมระบบ

### 5.1 Software Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Ground Control Station (PC)                │
│  - PyQt5/Tkinter GUI                                    │
│  - Real-time Telemetry Display                          │
│  - PID Tuning Interface                                 │
│  - Flight Data Logger                                   │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ WiFi/LoRa
                 │ (MAVLink Protocol)
                 ▼
┌─────────────────────────────────────────────────────────┐
│          Flight Controller (ESP32/STM32)                │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Main Control Loop (250Hz)               │   │
│  │  - Sensor Reading                               │   │
│  │  - Attitude Estimation (Kalman Filter)          │   │
│  │  - PID Controllers (Roll/Pitch/Yaw/Alt)         │   │
│  │  - Motor Mixing                                 │   │
│  │  - Servo Control                                │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────────────┘
                 │
         ┌───────┴────────┐
         │                │
         ▼                ▼
┌─────────────┐  ┌─────────────┐
│   4x ESC    │  │ 4x Servo    │
│  (Motor     │  │  (Thrust    │
│   Control)  │  │   Vector)   │
└──────┬──────┘  └──────┬──────┘
       │                │
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│ 4x BLDC     │  │ Vectoring   │
│   Motors    │  │ Mechanism   │
└─────────────┘  └─────────────┘
```

### 5.2 Control Loop Architecture

```
┌──────────────────────────────────────────────────────┐
│              Control Loop (250Hz)                    │
│                                                      │
│  ┌────────┐    ┌────────┐    ┌────────┐           │
│  │  IMU   │───▶│ Sensor │───▶│Attitude│           │
│  │ Read   │    │ Fusion │    │Estimate│           │
│  └────────┘    └────────┘    └────────┘           │
│                                   │                 │
│                                   ▼                 │
│  ┌────────┐    ┌────────┐    ┌────────┐           │
│  │ RC/GCS │───▶│  PID   │───▶│ Motor  │───▶ ESC   │
│  │Command │    │Control │    │ Mixing │           │
│  └────────┘    └────────┘    └────────┘           │
│                                   │                 │
│                                   ▼                 │
│  ┌────────┐                  ┌────────┐           │
│  │ Servo  │◀─────────────────│Vectoring│          │
│  │Control │                  │ Calc   │           │
│  └────────┘                  └────────┘           │
└──────────────────────────────────────────────────────┘
```

### 5.3 Communication Architecture

**MAVLink Protocol Stack:**

```
┌─────────────────────────────────────┐
│      Application Layer              │
│   - Telemetry Messages              │
│   - Command Messages                │
│   - Parameter Protocol              │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│       MAVLink Protocol              │
│   - Message Encoding/Decoding       │
│   - CRC Checking                    │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│     Transport Layer                 │
│   - WiFi UDP (Port 14550)           │
│   - LoRa Serial (57600 baud)        │
└─────────────────────────────────────┘
```

---

## 6. แผนภาพระบบ

### 6.1 Control Flow Diagram

```
┌────────────────────┐
│   Sensor Input     │
│ • IMU (Accel/Gyro) │
│ • Barometer        │
│ • RC/GCS Commands  │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Sensor Fusion     │
│  (Kalman Filter)   │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  PID Controllers   │
│  • Roll PID        │
│  • Pitch PID       │
│  • Yaw PID         │
│  • Altitude PID    │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Motor Mixing      │
│  Calculate speeds  │
└─────────┬──────────┘
          │
          ├────────────────┐
          │                │
          ▼                ▼
┌────────────────┐  ┌────────────────┐
│  ESC Output    │  │ Servo Control  │
│  PWM 1000-2000 │  │ Thrust Vector  │
└────────┬───────┘  └────────┬───────┘
         │                   │
         ▼                   ▼
┌────────────────┐  ┌────────────────┐
│ BLDC Motors    │  │ Servo Motors   │
└────────────────┘  └────────────────┘
```

### 6.2 State Machine Diagram

```
              ┌─────────────┐
              │   STANDBY   │◀────┐
              └──────┬──────┘     │
                     │ ARM         │ DISARM
                     ▼             │
              ┌─────────────┐     │
         ┌───▶│   ARMED     │─────┘
         │    └──────┬──────┘
         │           │ TAKEOFF
 LANDING │           ▼
         │    ┌─────────────┐
         └────│   FLYING    │
              └──────┬──────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
         ▼           ▼           ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │ MANUAL │ │STABILIZE│ │  AUTO  │
    └────────┘ └────────┘ └────────┘
```

---

## 7. วิธีการดำเนินงาน

### 7.1 Sensor Fusion Implementation

**Step 1: อ่านข้อมูลจาก IMU**

```python
import smbus
import time

class MPU6050:
    def __init__(self, bus=1, address=0x68):
        self.bus = smbus.SMBus(bus)
        self.address = address
        self.init_sensor()
    
    def read_accel(self):
        """อ่านค่า accelerometer"""
        raw_x = self.read_word_2c(0x3B)
        raw_y = self.read_word_2c(0x3D)
        raw_z = self.read_word_2c(0x3F)
        
        # แปลงเป็น g (±2g range)
        accel_x = raw_x / 16384.0
        accel_y = raw_y / 16384.0
        accel_z = raw_z / 16384.0
        
        return accel_x, accel_y, accel_z
    
    def read_gyro(self):
        """อ่านค่า gyroscope"""
        raw_x = self.read_word_2c(0x43)
        raw_y = self.read_word_2c(0x45)
        raw_z = self.read_word_2c(0x47)
        
        # แปลงเป็น deg/s (±250°/s range)
        gyro_x = raw_x / 131.0
        gyro_y = raw_y / 131.0
        gyro_z = raw_z / 131.0
        
        return gyro_x, gyro_y, gyro_z
```

**Step 2: Complementary Filter**

```python
class ComplementaryFilter:
    def __init__(self, alpha=0.98):
        self.alpha = alpha
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.last_time = time.time()
    
    def update(self, accel, gyro):
        """รวมข้อมูลจาก accel และ gyro"""
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        # คำนวณมุมจาก accelerometer
        accel_angle_x = math.atan2(accel[1], accel[2])
        accel_angle_y = math.atan2(-accel[0], math.sqrt(accel[1]**2 + accel[2]**2))
        
        # รวมกับ gyroscope
        self.angle_x = self.alpha * (self.angle_x + gyro[0] * dt) + (1-self.alpha) * accel_angle_x
        self.angle_y = self.alpha * (self.angle_y + gyro[1] * dt) + (1-self.alpha) * accel_angle_y
        
        return math.degrees(self.angle_x), math.degrees(self.angle_y)
```

### 7.2 PID Controller Implementation

```python
class PIDController:
    def __init__(self, kp, ki, kd, output_limits=(-100, 100)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_limits = output_limits
        
        self.integral = 0
        self.previous_error = 0
        self.last_time = time.time()
    
    def compute(self, setpoint, measured_value):
        """คำนวณ PID output"""
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        # คำนวณ error
        error = setpoint - measured_value
        
        # Proportional term
        p_term = self.kp * error
        
        # Integral term (anti-windup)
        self.integral += error * dt
        self.integral = self.constrain(self.integral, -50, 50)
        i_term = self.ki * self.integral
        
        # Derivative term
        derivative = (error - self.previous_error) / dt if dt > 0 else 0
        d_term = self.kd * derivative
        
        # Output
        output = p_term + i_term + d_term
        output = self.constrain(output, *self.output_limits)
        
        self.previous_error = error
        return output
    
    def reset(self):
        """รีเซ็ต PID"""
        self.integral = 0
        self.previous_error = 0
    
    @staticmethod
    def constrain(value, min_val, max_val):
        return max(min_val, min(max_val, value))
```

### 7.3 Motor Mixing และ Servo Control

**Step 1: Motor Mixing**

```python
def calculate_motor_outputs(throttle, roll_pid, pitch_pid, yaw_pid):
    """
    คำนวณ PWM สำหรับแต่ละ motor
    
    Motor Layout:
         Front
      M2     M1
        \ X /
        / X \
      M3     M4
         Back
    """
    # Mixing algorithm
    m1 = throttle + pitch_pid + roll_pid - yaw_pid  # Front-right
    m2 = throttle + pitch_pid - roll_pid + yaw_pid  # Front-left
    m3 = throttle - pitch_pid - roll_pid - yaw_pid  # Back-left
    m4 = throttle - pitch_pid + roll_pid + yaw_pid  # Back-right
    
    # Constrain to ESC range (1000-2000μs)
    motors = [
        constrain(m1, 1000, 2000),
        constrain(m2, 1000, 2000),
        constrain(m3, 1000, 2000),
        constrain(m4, 1000, 2000)
    ]
    
    return motors

def constrain(value, min_val, max_val):
    return max(min_val, min(max_val, value))
```

**Step 2: Thrust Vectoring Control**

```python
def calculate_servo_angles(roll_angle, pitch_angle, max_tilt=15):
    """
    คำนวณมุม servo สำหรับ thrust vectoring
    
    Servo Layout:
         Front
      S2     S1
        \ X /
        / X \
      S3     S4
         Back
    """
    # Normalize inputs
    roll_correction = constrain(roll_angle, -max_tilt, max_tilt)
    pitch_correction = constrain(pitch_angle, -max_tilt, max_tilt)
    
    # Base angle (90° = neutral position)
    base = 90
    
    # Calculate servo angles
    s1 = base - roll_correction + pitch_correction  # Front-right
    s2 = base + roll_correction + pitch_correction  # Front-left
    s3 = base + roll_correction - pitch_correction  # Back-left
    s4 = base - roll_correction - pitch_correction  # Back-right
    
    # Constrain to servo range (0-180°)
    servos = [
        constrain(s1, 0, 180),
        constrain(s2, 0, 180),
        constrain(s3, 0, 180),
        constrain(s4, 0, 180)
    ]
    
    return servos
```

**Step 3: PWM Output (ESP32)**

```cpp
// Arduino/ESP32 Code
#include <ESP32Servo.h>

Servo servo1, servo2, servo3, servo4;

void setup() {
    // ESC PWM pins (50Hz)
    ledcSetup(0, 50, 16);  // Channel 0, 50Hz, 16-bit resolution
    ledcAttachPin(25, 0);  // Motor 1
    ledcAttachPin(26, 1);  // Motor 2
    ledcAttachPin(27, 2);  // Motor 3
    ledcAttachPin(14, 3);  // Motor 4
    
    // Servo pins
    servo1.attach(32);  // Servo 1
    servo2.attach(33);  // Servo 2
    servo3.attach(18);  // Servo 3
    servo4.attach(19);  // Servo 4
}

void setMotorSpeed(int motor, int pwm) {
    // PWM: 1000-2000μs
    int dutyCycle = map(pwm, 1000, 2000, 3277, 6553);  // 16-bit
    ledcWrite(motor, dutyCycle);
}

void setServoAngle(Servo& servo, int angle) {
    // Angle: 0-180°
    servo.write(constrain(angle, 0, 180));
}
```

### 7.4 Communication Protocol Implementation

**Step 1: MAVLink Setup (Python GCS)**

```python
from pymavlink import mavutil
import time

class DroneConnection:
    def __init__(self, connection_string='udp:0.0.0.0:14550'):
        self.master = mavutil.mavlink_connection(connection_string)
        self.wait_heartbeat()
    
    def wait_heartbeat(self):
        """รอ heartbeat จาก drone"""
        print("Waiting for heartbeat...")
        self.master.wait_heartbeat()
        print(f"Heartbeat from system {self.master.target_system}")
    
    def send_attitude_setpoint(self, roll, pitch, yaw, thrust):
        """ส่งคำสั่งควบคุมทิศทาง"""
        self.master.mav.set_attitude_target_send(
            0,                          # time_boot_ms
            self.master.target_system,  # target system
            self.master.target_component,
            0b00000111,                 # type mask (ignore rates)
            self.to_quaternion(roll, pitch, yaw),
            0, 0, 0,                    # body roll rate, pitch rate, yaw rate
            thrust                      # thrust [0-1]
        )
    
    def receive_telemetry(self):
        """รับข้อมูล telemetry"""
        msg = self.master.recv_match(blocking=False)
        if msg:
            msg_type = msg.get_type()
            if msg_type == 'ATTITUDE':
                return {
                    'roll': msg.roll,
                    'pitch': msg.pitch,
                    'yaw': msg.yaw,
                    'rollspeed': msg.rollspeed,
                    'pitchspeed': msg.pitchspeed,
                    'yawspeed': msg.yawspeed
                }
        return None
```

**Step 2: Ground Control Station GUI**

```python
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class GroundControlStation:
    def __init__(self, root):
        self.root = root
        self.root.title("Thrust Vectoring Drone GCS")
        self.drone = DroneConnection()
        
        self.create_widgets()
        self.update_telemetry()
    
    def create_widgets(self):
        # Control Panel
        control_frame = ttk.LabelFrame(self.root, text="Manual Control")
        control_frame.grid(row=0, column=0, padx=10, pady=10)
        
        # Throttle slider
        ttk.Label(control_frame, text="Throttle:").grid(row=0, column=0)
        self.throttle_slider = ttk.Scale(control_frame, from_=0, to=100, orient='vertical')
        self.throttle_slider.grid(row=1, column=0)
        
        # Roll/Pitch control
        ttk.Label(control_frame, text="Roll/Pitch:").grid(row=0, column=1)
        self.attitude_canvas = tk.Canvas(control_frame, width=200, height=200, bg='white')
        self.attitude_canvas.grid(row=1, column=1)
        self.attitude_canvas.bind('<B1-Motion>', self.on_attitude_drag)
        
        # Telemetry Display
        telemetry_frame = ttk.LabelFrame(self.root, text="Telemetry")
        telemetry_frame.grid(row=0, column=1, padx=10, pady=10)
        
        self.telemetry_labels = {}
        for i, param in enumerate(['Roll', 'Pitch', 'Yaw', 'Altitude', 'Battery']):
            ttk.Label(telemetry_frame, text=f"{param}:").grid(row=i, column=0, sticky='w')
            label = ttk.Label(telemetry_frame, text="0.0")
            label.grid(row=i, column=1, sticky='w')
            self.telemetry_labels[param] = label
        
        # Attitude Indicator
        attitude_frame = ttk.LabelFrame(self.root, text="Attitude")
        attitude_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        self.fig, self.ax = plt.subplots(figsize=(6, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=attitude_frame)
        self.canvas.get_tk_widget().pack()
        
        # PID Tuning
        pid_frame = ttk.LabelFrame(self.root, text="PID Tuning")
        pid_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        
        self.pid_entries = {}
        for i, axis in enumerate(['Roll', 'Pitch', 'Yaw']):
            ttk.Label(pid_frame, text=f"{axis}:").grid(row=i, column=0)
            for j, param in enumerate(['P', 'I', 'D']):
                entry = ttk.Entry(pid_frame, width=10)
                entry.grid(row=i, column=j+1)
                self.pid_entries[f"{axis}_{param}"] = entry
        
        ttk.Button(pid_frame, text="Update PID", command=self.update_pid).grid(row=3, column=0, columnspan=4)
    
    def update_telemetry(self):
        """อัพเดท telemetry display"""
        telemetry = self.drone.receive_telemetry()
        if telemetry:
            self.telemetry_labels['Roll'].config(text=f"{np.degrees(telemetry['roll']):.1f}°")
            self.telemetry_labels['Pitch'].config(text=f"{np.degrees(telemetry['pitch']):.1f}°")
            self.telemetry_labels['Yaw'].config(text=f"{np.degrees(telemetry['yaw']):.1f}°")
            
            # Update attitude plot
            self.plot_attitude(telemetry)
        
        self.root.after(50, self.update_telemetry)  # Update at 20Hz
    
    def plot_attitude(self, telemetry):
        """Plot attitude indicator"""
        self.ax.clear()
        roll = np.degrees(telemetry['roll'])
        pitch = np.degrees(telemetry['pitch'])
        
        # Draw horizon
        self.ax.plot([-1, 1], [pitch/90, pitch/90], 'b-', linewidth=2)
        
        # Draw roll indicator
        self.ax.plot([0, 0.5*np.sin(telemetry['roll'])], 
                     [0, 0.5*np.cos(telemetry['roll'])], 'r-', linewidth=3)
        
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_aspect('equal')
        self.ax.grid(True)
        self.canvas.draw()
    
    def on_attitude_drag(self, event):
        """Handle attitude control drag"""
        x = (event.x - 100) / 100  # Normalize to [-1, 1]
        y = -(event.y - 100) / 100
        
        roll = x * 30  # Max 30° roll
        pitch = y * 30  # Max 30° pitch
        
        throttle = self.throttle_slider.get()
        self.drone.send_attitude_setpoint(
            np.radians(roll),
            np.radians(pitch),
            0,  # Yaw rate
            throttle / 100
        )
    
    def update_pid(self):
        """ส่งค่า PID ไปยัง drone"""
        # Implementation for sending PID parameters
        pass

if __name__ == '__main__':
    root = tk.Tk()
    app = GroundControlStation(root)
    root.mainloop()
```

---

## 8. การใช้งาน

### 8.1 ความต้องการของระบบ

**Hardware:**

```
- ESP32/STM32 Development Board
- IMU Module (MPU6050/MPU9250)
- 4x Brushless Motors (1000-1500KV)
- 4x ESC (20A-30A)
- 4x Servo Motors (MG90S or similar)
- 3S LiPo Battery (2200-3000mAh)
- RC Receiver (Optional)
- Frame และ mechanical parts
```

**Software:**

```
Python 3.8 or higher
Arduino IDE / PlatformIO
```

**Python Libraries:**

```bash
pip install pymavlink
pip install pyserial
pip install numpy
pip install matplotlib
pip install PyQt5
pip install smbus2
```

**Arduino Libraries:**

```
ESP32Servo
Wire (I2C)
WiFi
MAVLink
```

### 8.2 การติดตั้ง

**Step 1: Clone Repository**

```bash
git clone https://github.com/yourusername/thrust-vectoring-drone.git
cd thrust-vectoring-drone
```

**Step 2: ติดตั้ง Dependencies**

```bash
# Python dependencies
pip install -r requirements.txt

# Arduino libraries (ติดตั้งผ่าน Arduino Library Manager)
```

**Step 3: Upload Firmware**

```bash
# เปิดไฟล์ flight_controller.ino ใน Arduino IDE
# เลือก Board: ESP32 Dev Module
# เลือก Port และ Upload
```

**Step 4: กำหนดค่า WiFi**

```cpp
// ในไฟล์ config.h
#define WIFI_SSID "your_wifi_name"
#define WIFI_PASSWORD "your_password"
#define GCS_IP "192.168.1.100"  // IP ของ Ground Station
```

### 8.3 การปรับแต่ง

**Calibrate IMU:**

1. วาง drone บนพื้นราบ
2. เปิด Serial Monitor
3. ส่งคำสั่ง "CAL" เพื่อ calibrate accelerometer
4. หมุน drone ในทุกทิศทางเพื่อ calibrate magnetometer

**Tune PID Parameters:**

1. เริ่มจากค่า conservative (P=1.0, I=0.0, D=0.0)
2. เพิ่ม P จนกว่า drone จะเริ่ม oscillate
3. ลด P ลง 30% และเพิ่ม D เพื่อลด overshoot
4. เพิ่ม I เล็กน้อยเพื่อแก้ steady-state error
5. ทดสอบและปรับแต่งจนได้ response ที่ต้องการ

**ESC Calibration:**

```
1. ปิด power ทั้งหมด
2. ตั้ง throttle เป็น maximum
3. เปิด power
4. รอเสียง beep
5. ตั้ง throttle เป็น minimum
6. รอเสียง confirmation
7. ทดสอบ throttle range
```

### 8.4 การใช้งานระบบ

**Mode การบิน:**

1. **STANDBY**: ระบบพร้อม, motors ปิด
2. **ARMED**: ระบบ armed, motors idle
3. **STABILIZE**: ควบคุมด้วย PID, pilot controls attitude
4. **ALTITUDE HOLD**: รักษาความสูง
5. **MANUAL**: ควบคุมแบบ manual (no stabilization)

**การบิน:**

```
1. เปิด Ground Control Station
2. เชื่อมต่อกับ drone (WiFi)
3. ตรวจสอบ telemetry และ sensors
4. Arm motors (Safety switch)
5. เพิ่ม throttle ค่อย ๆ สำหรับ takeoff
6. ควบคุมด้วย attitude commands
7. Landing: ลด throttle ค่อย ๆ
8. Disarm motors
```

**การใช้ GCS:**

```
1. เปิดโปรแกรม:
   python ground_control_station.py

2. กรอก IP ของ drone
3. กดปุ่ม "Connect"
4. Monitor telemetry แบบ real-time
5. ปรับแต่ง PID parameters (ถ้าต้องการ)
6. ส่งคำสั่งผ่าน manual control หรือ RC
7. Save flight logs สำหรับวิเคราะห์
```

**Safety Features:**

- Low battery warning (< 10.5V)
- Failsafe (loss of signal → land mode)
- Emergency stop (kill switch)
- Angle limits (roll/pitch < 45°)
- Auto-disarm (no movement for 5s)

### 8.5 Troubleshooting

**ปัญหาที่พบบ่อย:**

| ปัญหา | สาเหตุที่เป็นไปได้ | แก้ไข |
|-------|------------------|------|
| Drone ไม่ตอบสนอง | ไม่ได้ arm motors | กด safety switch |
| Oscillation | PID values สูงเกินไป | ลด P และ D |
| Drift | IMU not calibrated | Calibrate IMU ใหม่ |
| One motor ไม่หมุน | ESC/Motor failure | ตรวจสอบ connections |
| Connection lost | WiFi signal weak | ลดระยะห่าง หรือใช้ LoRa |

**Debug Mode:**

```cpp
// Enable debug output
#define DEBUG_MODE 1

// ใน Serial Monitor จะแสดง:
// - Sensor values
// - PID outputs
// - Motor speeds
// - Servo angles
```

---

## ผู้พัฒนา

- **ชื่อ นามสกุล** - รหัสนักศึกษา 664XXXXXXX
- **ชื่อ นามสกุล** - รหัสนักศึกษา 664XXXXXXX

---

## License

This project is licensed under the MIT License - see the LICENSE file for details

---

## Acknowledgments

- Robotics Toolbox for Python
- PX4 และ ArduPilot communities
- MAVLink Protocol developers
- ESP32 Arduino Core

---

## อ้างอิง

1. Stevens, B. L., & Lewis, F. L. (2003). *Aircraft Control and Simulation*. Wiley.
2. Beard, R. W., & McLain, T. W. (2012). *Small Unmanned Aircraft: Theory and Practice*. Princeton University Press.
3. Mahony, R., et al. (2008). "Nonlinear Complementary Filters on the Special Orthogonal Group". *IEEE TAC*.
4. MAVLink Documentation: https://mavlink.io/
5. PX4 Developer Guide: https://dev.px4.io/
message.txt
message.txt (41 KB)
41 KB
