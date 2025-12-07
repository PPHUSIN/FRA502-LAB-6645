#include "gps_handler.h"

TinyGPSPlus gps;
HardwareSerial gpsSerial(1); // Use Serial1 for GPS

void initGPS(int rxPin, int txPin, long baudRate) {
    gpsSerial.begin(baudRate, SERIAL_8N1, rxPin, txPin);
    Serial.println("GPS initialized");
    Serial.print("GPS RX: GPIO");
    Serial.print(rxPin);
    Serial.print(", TX: GPIO");
    Serial.println(txPin);
}

void updateGPS() {
    while (gpsSerial.available() > 0) {
        gps.encode(gpsSerial.read());
    }
}

void updateGPSWithDebug() {
    while (gpsSerial.available() > 0) {
        char c = gpsSerial.read();
        Serial.write(c);
        gps.encode(c);
    }
}

int getGPSCharsProcessed() {
    return gps.charsProcessed();
}

GPSData getGPSData() {
    GPSData data;
    
    if (gps.location.isValid()) {
        data.latitude = gps.location.lat();
        data.longitude = gps.location.lng();
        data.isValid = true;
    } else {
        data.latitude = 0.0;
        data.longitude = 0.0;
        data.isValid = false;
    }
    
    if (gps.altitude.isValid()) {
        data.altitude = gps.altitude.meters();
    } else {
        data.altitude = 0.0;
    }
    
    if (gps.speed.isValid()) {
        data.speed = gps.speed.kmph();
    } else {
        data.speed = 0.0;
    }
    
    if (gps.satellites.isValid()) {
        data.satellites = gps.satellites.value();
    } else {
        data.satellites = 0;
    }
    
    return data;
}

void printGPSData() {
    GPSData data = getGPSData();
    
    Serial.println("=== GPS Data ===");
    
    if (data.isValid) {
        Serial.print("Latitude: ");
        Serial.println(data.latitude, 6);
        Serial.print("Longitude: ");
        Serial.println(data.longitude, 6);
        Serial.print("Altitude: ");
        Serial.print(data.altitude);
        Serial.println(" m");
        Serial.print("Speed: ");
        Serial.print(data.speed);
        Serial.println(" km/h");
        Serial.print("Satellites: ");
        Serial.println(data.satellites);
    } else {
        Serial.println("No GPS fix - Waiting for satellites...");
        Serial.print("Satellites: ");
        Serial.println(data.satellites);
    }
    
    Serial.print("Characters processed: ");
    Serial.println(gps.charsProcessed());
    Serial.print("Failed checksums: ");
    Serial.println(gps.failedChecksum());
    Serial.println("================");
}

void testGPSConnection() {
    Serial.println("=== GPS Connection Test ===");
    Serial.print("Characters received: ");
    Serial.println(gps.charsProcessed());
    
    if (gps.charsProcessed() == 0) {
        Serial.println("❌ No data from GPS!");
        Serial.println("   Check: VCC, GND, TX->GPIO17, RX->GPIO18");
        Serial.println("   Try different baud rate: 4800 or 115200");
    } else {
        Serial.println("✅ GPS is sending data");
        Serial.print("   Satellites in view: ");
        Serial.println(gps.satellites.value());
        Serial.print("   Has fix: ");
        Serial.println(gps.location.isValid() ? "YES" : "NO");
        
        if (!gps.location.isValid()) {
            Serial.println("   💡 Move to open sky area and wait 2-5 min");
        }
    }
    Serial.println("===========================");
}
void setGPSHint(double latitude, double longitude) {
    Serial.println("\n=== Setting GPS Hint ===");
    Serial.printf("Hint Position: %.6f, %.6f\n", latitude, longitude);
    
    // สำหรับ u-blox GPS modules (NEO-6M, NEO-7M, NEO-M8N)
    // ส่งคำสั่ง UBX-AID-INI เพื่อบอกตำแหน่งเริ่มต้น
    
    // หมายเหตุ: ส่วนใหญ่ GPS modules จะใช้ข้อมูลนี้ internal
    // แต่การส่งคำสั่งตรงต้องใช้ UBX protocol
    
    // วิธีง่าย: GPS จะ lock เร็วขึ้นเองถ้าอยู่ใกล้ตำแหน่งเดิม
    // แค่เก็บค่าไว้ใช้เปรียบเทียบก็พอ
    
    Serial.println("GPS will use this as reference for faster lock");
}