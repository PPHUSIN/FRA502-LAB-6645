#include <imu.h>

// ============================================
// imu.cpp - Implementation File
// ============================================

MPU9250_IMU::MPU9250_IMU() {
    accelX = accelY = accelZ = 0;
    gyroX = gyroY = gyroZ = 0;
    rawAccelX = rawAccelY = rawAccelZ = 0;
    rawGyroX = rawGyroY = rawGyroZ = 0;
    roll = pitch = yaw = 0;
    lastTime = 0;
    
    // ⚙️ ตั้งค่า default rotation ที่นี่
    // rotation = ROTATION_90_CW;  // สำหรับ Y-axis = Forward
    rotation = ROTATION_0;
}

void MPU9250_IMU::setRotation(IMU_ROTATION rot) {
    rotation = rot;
    Serial.print("IMU Rotation set to: ");
    switch(rot) {
        case ROTATION_0:
            Serial.println("0° (X=Forward)");
            break;
        case ROTATION_90_CW:
            Serial.println("90° CW (Y=Forward)");
            break;
        case ROTATION_90_CCW:
            Serial.println("90° CCW (-Y=Forward)");
            break;
        case ROTATION_180:
            Serial.println("180° (-X=Forward)");
            break;
        case ROTATION_UPSIDE_DOWN:
            Serial.println("Upside Down");
            break;
    }
}

void MPU9250_IMU::applyRotation() {
    float tempAx = rawAccelX;
    float tempAy = rawAccelY;
    float tempAz = rawAccelZ;
    float tempGx = rawGyroX;
    float tempGy = rawGyroY;
    float tempGz = rawGyroZ;
    
    switch(rotation) {
        case ROTATION_0:
            accelX = tempAx;
            accelY = tempAy;
            accelZ = tempAz;
            gyroX = tempGx;
            gyroY = tempGy;
            gyroZ = tempGz;
            break;
            
        case ROTATION_90_CW:
            accelX = -tempAy;
            accelY = tempAx;
            accelZ = tempAz;
            gyroX = -tempGy;
            gyroY = tempGx;
            gyroZ = tempGz;
            break;
            
        case ROTATION_90_CCW:
            accelX = tempAy;
            accelY = -tempAx;
            accelZ = tempAz;
            gyroX = tempGy;
            gyroY = -tempGx;
            gyroZ = tempGz;
            break;
            
        case ROTATION_180:
            accelX = -tempAx;
            accelY = -tempAy;
            accelZ = tempAz;
            gyroX = -tempGx;
            gyroY = -tempGy;
            gyroZ = tempGz;
            break;
            
        case ROTATION_UPSIDE_DOWN:
            accelX = tempAx;
            accelY = -tempAy;
            accelZ = -tempAz;
            gyroX = tempGx;
            gyroY = -tempGy;
            gyroZ = -tempGz;
            break;
            
        // ============================================
        // 🔧 CUSTOM ROTATIONS - ลองทีละอันจนเจอที่ถูก
        // ============================================
        
        case ROTATION_CUSTOM_1: // Z ชี้ Forward
            accelX = tempAz;
            accelY = tempAx;
            accelZ = -tempAy;
            gyroX = tempGz;
            gyroY = tempGx;
            gyroZ = -tempGy;
            break;
            
        case ROTATION_CUSTOM_2: // -Z ชี้ Forward
            accelX = -tempAz;
            accelY = tempAx;
            accelZ = tempAy;
            gyroX = -tempGz;
            gyroY = tempGx;
            gyroZ = tempGy;
            break;
            
        case ROTATION_CUSTOM_3: 
            // --- Accelerometer ---
            accelX =  tempAy;
            accelY =  tempAz;
            accelZ = -tempAx;

            // --- Gyroscope ---
            gyroX  = -tempGy;   // กลับเครื่องหมาย roll
            gyroY  =  tempGz;
            gyroZ  =  tempGx;   // กลับให้ yaw หมุนขวาเป็นบวก
            break;
            
        case ROTATION_CUSTOM_4: // -Z ชี้ Forward, Y ชี้ Right
            accelX = -tempAz;
            accelY = tempAy;
            accelZ = tempAx;
            gyroX = -tempGz;
            gyroY = tempGy;
            gyroZ = tempGx;
            break;
            
        case ROTATION_CUSTOM_5: // X ชี้ Right, Z ชี้ Forward
            accelX = tempAz;
            accelY = -tempAy;
            accelZ = tempAx;
            gyroX = tempGz;
            gyroY = -tempGy;
            gyroZ = tempGx;
            break;
            
        case ROTATION_CUSTOM_6: // -X ชี้ Right, Z ชี้ Forward
            accelX = tempAz;
            accelY = tempAy;
            accelZ = tempAx;
            gyroX = tempGz;
            gyroY = tempGy;
            gyroZ = tempGx;
            break;
    }
}


void MPU9250_IMU::writeMPU(uint8_t reg, uint8_t data) {
    Wire.beginTransmission(MPU9250_ADDR);
    Wire.write(reg);
    Wire.write(data);
    Wire.endTransmission();
}

uint8_t MPU9250_IMU::readMPU(uint8_t reg) {
    Wire.beginTransmission(MPU9250_ADDR);
    Wire.write(reg);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU9250_ADDR, 1);
    return Wire.read();
}

void MPU9250_IMU::readMPUData(uint8_t reg, int16_t* data, uint8_t count) {
    Wire.beginTransmission(MPU9250_ADDR);
    Wire.write(reg);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU9250_ADDR, count * 2);
    
    for (uint8_t i = 0; i < count; i++) {
        data[i] = (Wire.read() << 8) | Wire.read();
    }
}
void MPU9250_IMU::zeroOrientation() {
    rollOffset = roll;
    pitchOffset = pitch;
    yawOffset = yaw;
    Serial.println("✅ IMU orientation zeroed!");
}
bool MPU9250_IMU::begin() {
    // ตรวจสอบ WHO_AM_I
    uint8_t whoami = readMPU(WHO_AM_I);
    Serial.print("WHO_AM_I: 0x");
    Serial.println(whoami, HEX);
    
    // MPU9250 = 0x71, MPU9255 = 0x73, MPU6500 = 0x70, MPU6050 = 0x68
    if (whoami != 0x71 && whoami != 0x73 && whoami != 0x70 && whoami != 0x68) {
        Serial.println("WHO_AM_I ไม่ตรงกับ MPU series!");
        return false;
    }
    
    if (whoami == 0x70) {
        Serial.println("พบ MPU6500 (6-axis: Accel + Gyro)");
    } else if (whoami == 0x68) {
        Serial.println("พบ MPU6050 (6-axis: Accel + Gyro)");
    } else {
        Serial.println("พบ MPU9250/9255 (9-axis: Accel + Gyro + Mag)");
    }
    
    // Reset MPU9250
    writeMPU(PWR_MGMT_1, 0x80);
    delay(100);
    
    // Wake up และตั้งค่า clock
    writeMPU(PWR_MGMT_1, 0x01);
    delay(100);
    
    // ตั้งค่า Gyro range ±250 deg/s
    writeMPU(0x1B, 0x00);
    
    // ตั้งค่า Accel range ±2g
    writeMPU(0x1C, 0x00);
    
    lastTime = millis();
    
    Serial.println("✅ MPU9250 เริ่มต้นสำเร็จ!");
    setRotation(rotation); // แสดง rotation ที่ตั้งไว้
    
    return true;
}

void MPU9250_IMU::readSensorData() {
    int16_t rawData[6];
    
    // อ่าน Accelerometer (raw data)
    readMPUData(ACCEL_XOUT_H, rawData, 3);
    rawAccelX = rawData[0] / 16384.0;  // ±2g
    rawAccelY = rawData[1] / 16384.0;
    rawAccelZ = rawData[2] / 16384.0;
    
    // อ่าน Gyroscope (raw data)
    readMPUData(GYRO_XOUT_H, rawData, 3);
    rawGyroX = rawData[0] / 131.0;  // ±250 deg/s
    rawGyroY = rawData[1] / 131.0;
    rawGyroZ = rawData[2] / 131.0;
    
    applyRotation();
}

void MPU9250_IMU::calculateOrientation() {
    unsigned long currentTime = millis();
    float dt = (currentTime - lastTime) / 1000.0;
    lastTime = currentTime;
    
    float accelRoll = atan2(accelY, accelZ) * 180.0 / PI;
    float accelPitch = atan2(-accelX, sqrt(accelY * accelY + accelZ * accelZ)) * 180.0 / PI;
    
    roll = 0.98 * (roll + gyroX * dt) + 0.02 * accelRoll;
    pitch = 0.98 * (pitch + gyroY * dt) + 0.02 * accelPitch;


    yaw += gyroZ * dt; 


    float displayRoll = roll - rollOffset;
    float displayPitch = pitch - pitchOffset;
    float displayYaw = yaw - yawOffset;

    while (displayYaw >= 360.0) displayYaw -= 360.0;
    while (displayYaw < 0.0) displayYaw += 360.0;
    

    roll = displayRoll; 

}

// ============================================
// 🧪 TESTING & CALIBRATION FUNCTIONS
// ============================================

void MPU9250_IMU::testRotation(int samples) {
    Serial.println("\n╔════════════════════════════════════════╗");
    Serial.println("║   🧭 IMU ROTATION TEST                ║");
    Serial.println("╚════════════════════════════════════════╝");
    Serial.println("Place drone FLAT and LEVEL, then observe:");
    Serial.println("Expected: Roll ≈ 0°, Pitch ≈ 0°\n");
    
    delay(2000);
    
    for(int i = 0; i < samples; i++) {
        readSensorData();
        calculateOrientation();
        
        Serial.printf("[%2d/%2d] Roll: %6.1f°  Pitch: %6.1f°  Yaw: %6.1f°\n", 
                     i+1, samples, roll, pitch, yaw);
        
        delay(100);
    }
    
    Serial.println("\n✓ Test complete!");
    Serial.println("\n📋 If Roll/Pitch are NOT near 0° when flat:");
    Serial.println("   1. Try different rotation mode:");
    Serial.println("      imu.setRotation(ROTATION_90_CW);");
    Serial.println("      imu.setRotation(ROTATION_90_CCW);");
    Serial.println("      imu.setRotation(ROTATION_180);");
    Serial.println("   2. Re-run testRotation()");
    Serial.println();
}

void MPU9250_IMU::printOrientation() {
    Serial.println("\n╔════════════════════════════════════════╗");
    Serial.println("║   🎯 IMU ORIENTATION GUIDE            ║");
    Serial.println("╚════════════════════════════════════════╝");
    Serial.println();
    Serial.println("Test 1: Tilt NOSE UP (Forward)");
    Serial.println("  → Pitch should be POSITIVE (+)");
    Serial.println();
    Serial.println("Test 2: Tilt RIGHT SIDE DOWN");
    Serial.println("  → Roll should be POSITIVE (+)");
    Serial.println();
    Serial.println("Test 3: Rotate CLOCKWISE (top view)");
    Serial.println("  → Yaw should INCREASE");
    Serial.println();
    Serial.println("╔════════════════════════════════════════╗");
    Serial.println("║   📐 ROTATION MODES QUICK REF         ║");
    Serial.println("╠════════════════════════════════════════╣");
    Serial.println("║ X-axis → Forward   : ROTATION_0       ║");
    Serial.println("║ Y-axis → Forward   : ROTATION_90_CW   ║ ✓ Your IMU");
    Serial.println("║ -X-axis → Forward  : ROTATION_180     ║");
    Serial.println("║ -Y-axis → Forward  : ROTATION_90_CCW  ║");
    Serial.println("╚════════════════════════════════════════╝");
    Serial.println();
}


void MPU9250_IMU::testAllRotationsComplete() {
    Serial.println("\n╔════════════════════════════════════════╗");
    Serial.println("║   🔍 COMPLETE ROTATION TEST           ║");
    Serial.println("╚════════════════════════════════════════╝");
    Serial.println("Testing ALL possible rotations...");
    Serial.println("Keep drone FLAT and LEVEL!\n");
    
    IMU_ROTATION modes[] = {
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
    };
    
    const char* names[] = {
        "ROTATION_0",
        "ROTATION_90_CW",
        "ROTATION_90_CCW",
        "ROTATION_180",
        "ROTATION_UPSIDE_DOWN",
        "ROTATION_CUSTOM_1 (Z→Fwd)",
        "ROTATION_CUSTOM_2 (-Z→Fwd)",
        "ROTATION_CUSTOM_3 (Z→Fwd,Y→R)",
        "ROTATION_CUSTOM_4 (-Z→Fwd,Y→R)",
        "ROTATION_CUSTOM_5 (X→R,Z→Fwd)",
        "ROTATION_CUSTOM_6 (-X→R,Z→Fwd)"
    };
    
    int bestMode = -1;
    float bestError = 999;
    
    for(int mode = 0; mode < 11; mode++) {
        setRotation(modes[mode]);
        delay(300);
        
        // ทดสอบ 5 ตัวอย่าง
        float avgRoll = 0, avgPitch = 0;
        for(int i = 0; i < 5; i++) {
            readSensorData();
            calculateOrientation();
            avgRoll += roll;
            avgPitch += pitch;
            delay(50);
        }
        
        avgRoll /= 5;
        avgPitch /= 5;
        
        float error = abs(avgRoll) + abs(avgPitch);
        
        Serial.printf("[%2d] %-25s → R:%6.1f° P:%6.1f° Err:%.1f", 
                     mode+1, names[mode], avgRoll, avgPitch, error);
        
        if(error < 10) {
            Serial.print(" ✅ GOOD!");
            if(error < bestError) {
                bestError = error;
                bestMode = mode;
            }
        } else if(error < 20) {
            Serial.print(" ⚠️  OK");
        } else {
            Serial.print(" ❌");
        }
        Serial.println();
    }
    
    Serial.println("\n╔════════════════════════════════════════╗");
    Serial.println("║   🎯 RESULT                           ║");
    Serial.println("╚════════════════════════════════════════╝");
    
    if(bestMode >= 0) {
        Serial.printf("✅ BEST ROTATION: %s\n", names[bestMode]);
        Serial.printf("   Error: %.1f degrees\n", bestError);
        Serial.printf("\n👉 Add this to your setup():\n");
        Serial.printf("   imu.setRotation(%s);\n", names[bestMode]);
    } else {
        Serial.println("❌ No good rotation found!");
        Serial.println("   Check IMU mounting or try manual adjustment");
    }
    Serial.println();
}
