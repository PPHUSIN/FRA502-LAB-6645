// ============================================
// imu.h - Updated Header File
// ============================================
#ifndef IMU_H
#define IMU_H

#include <Arduino.h>
#include <Wire.h>

// MPU9250 registers
#define MPU9250_ADDR 0x68
#define PWR_MGMT_1   0x6B
#define ACCEL_XOUT_H 0x3B
#define GYRO_XOUT_H  0x43
#define WHO_AM_I     0x75

// ============================================
// 🧭 IMU ROTATION MODES
// ============================================
typedef enum {
    ROTATION_0,
    ROTATION_90_CW,
    ROTATION_90_CCW,
    ROTATION_180,
    ROTATION_UPSIDE_DOWN,
    ROTATION_CUSTOM_1,
    ROTATION_CUSTOM_2,
    ROTATION_CUSTOM_3,
    ROTATION_CUSTOM_4,
    ROTATION_CUSTOM_5,
    ROTATION_CUSTOM_6
} IMU_ROTATION;
class MPU9250_IMU {
public:
    // Sensor data (หลังแปลงแกนแล้ว)
    float accelX, accelY, accelZ;
    float gyroX, gyroY, gyroZ;
    float roll, pitch, yaw;
    
    float rollOffset, pitchOffset, yawOffset;

    // Raw data ก่อนแปลงแกน (สำหรับ debug)
    float rawAccelX, rawAccelY, rawAccelZ;
    float rawGyroX, rawGyroY, rawGyroZ;
    
    // Rotation setting
    IMU_ROTATION rotation;
    
    MPU9250_IMU();
    bool begin();
    void readSensorData();
    void calculateOrientation();
    void zeroOrientation();
    // ⚙️ Rotation control functions
    void setRotation(IMU_ROTATION rot);
    void testAllRotationsComplete();
    void testRotation(int samples = 50);
    void printOrientation();
    
private:
    unsigned long lastTime;
    
    void writeMPU(uint8_t reg, uint8_t data);
    uint8_t readMPU(uint8_t reg);
    void readMPUData(uint8_t reg, int16_t* data, uint8_t count);
    void applyRotation();  // ฟังก์ชันแปลงแกน
};

#endif