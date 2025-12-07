#ifndef ACTUATOR_H
#define ACTUATOR_H

#include <Arduino.h>
#include <ESP32Servo.h>

class ROVController {
public:
    // Constructor
    ROVController();
    
    // เริ่มต้นระบบ
    void begin();
    
    // เรียกใน loop() เพื่ออ่านคำสั่งและอัปเดต servo
    void update();
    
    // คำสั่งควบคุมแบบ manual
    void setServo(int servoNum, int offset);      // servo 1-4, offset -10 ถึง +10
    void setThruster(int power);                   // 0-100%
    void setAllServos(int offset);                 // ตั้งค่า servo 1-4 พร้อมกัน
    void moveToCenter();                           // กลับไปจุดกลาง
    void stop();                                   // หยุด thruster
    void showStatus();                             // แสดงสถานะปัจจุบัน
    
    // ตั้งค่า center position (ถ้าต้องการปรับ)
    void setCenterPositions(int c1, int c2, int c3, int c4);
    
    // ตั้งค่า pin (เรียกก่อน begin() ถ้าต้องการเปลี่ยน)
    void setPins(int pin1, int pin2, int pin3, int pin4, int pin5);
    
    // อ่านค่าปัจจุบัน
    int getCurrentServo(int servoNum);
    int getCurrentThruster();

private:
    // Servo objects
    Servo servo1, servo2, servo3, servo4, servo5;
    
    // Pins
    int PIN_1, PIN_2, PIN_3, PIN_4, PIN_5;
    
    // Center positions
    int CENTER_1, CENTER_2, CENTER_3, CENTER_4;
    
    // Constants
    static const int RANGE = 10;
    static const int THRUSTER_MIN = 0;
    static const int THRUSTER_MAX = 100;
    
    // Current positions
    int current1, current2, current3, current4, current5;
    
    // Target positions
    int target1, target2, target3, target4, target5;
    
    // Private methods
    void updateServos();
    void processSerialCommand();
    void parseSetCommand(String cmd);
};

#endif