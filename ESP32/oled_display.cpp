#include "oled_display.h"

Adafruit_SH1106G display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

uint8_t currentPage = 0;
const uint8_t MAX_PAGES = 3;  // เปลี่ยนจาก 2 เป็น 3 หน้า

void initDisplay() {

    Serial.print("I2C initialized - SDA:");
    Serial.print(OLED_SDA);
    Serial.print(" SCL:");
    Serial.println(OLED_SCL);
    
    if(!display.begin(SCREEN_ADDRESS, true)) {
        Serial.println(F("SH1106 allocation failed"));
        return;
    }
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SH110X_WHITE);
    display.setCursor(0, 0);
    display.println(F("ESP32-S3 GPS"));
    display.println(F("Initializing..."));
    display.display();
    delay(2000);
}

void displayGPSPage() {
    GPSData gpsData = getGPSData();
    
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(0, 0);
    
    // Header
    display.println(F("=== GPS DATA ==="));
    
    // GPS Status - แสดงดาวเทียมเสมอ
    display.print(F("SAT: "));
    display.print(gpsData.satellites);
    
    if (gpsData.isValid) {
        display.println(F(" LOCKED"));
    } else if (gpsData.satellites > 0) {
        display.println(F(" SEARCH"));
    } else {
        display.println(F(" NO SIG"));
    }
    
    // Coordinates
    display.print(F("Lat: "));
    if (gpsData.isValid) {
        display.println(gpsData.latitude, 6);
    } else {
        display.println(F("Waiting..."));
    }
    
    display.print(F("Lon: "));
    if (gpsData.isValid) {
        display.println(gpsData.longitude, 6);
    } else {
        display.println(F("Waiting..."));
    }
    
    // Altitude
    display.print(F("Alt: "));
    if (gpsData.isValid) {
        display.print(gpsData.altitude, 1);
        display.println(F("m"));
    } else {
        display.println(F("---"));
    }
    
    // Speed
    display.print(F("Spd: "));
    if (gpsData.isValid) {
        display.print(gpsData.speed, 1);
        display.println(F("km/h"));
    } else {
        display.println(F("---"));
    }
    
    display.display();
}

void displayWiFiPage(const char* ssid, bool wifi_status, bool agent_status) {
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(0, 0);
    
    // Header
    display.println(F("=== WiFi INFO ==="));
    
    // WiFi Status
    if (wifi_status) {
        display.println(F("Status: CONNECTED"));
        
        // SSID
        display.print(F("SSID: "));
        display.println(ssid);
        
        // Agent Status
        display.print(F("ROS Agent: "));
        if (agent_status) {
            display.println(F("OK"));
        } else {
            display.println(F("DISC"));
        }
    } else {
        display.println(F("Status: DISCONNECTED"));
        display.println(F("Reconnecting..."));
    }
    
    display.display();
}

void displayPositionPage(GPSData gpsData) {
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(0, 0);
    
    display.println(F("=== POSITION ==="));
    
    // GPS Status
    display.print(F("GPS: "));
    if (gpsData.isValid) {
        display.print(gpsData.satellites);
        display.println(F(" LOCK"));
    } else {
        display.print(gpsData.satellites);
        display.println(F(" SAT"));
    }
    
    display.display();
}

void updateDisplay() {
    // This function is called from main loop with parameters
}

void switchDisplayPage() {
    currentPage = (currentPage + 1) % MAX_PAGES;
}

void showMessage(const char* line1, const char* line2, const char* line3) {
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(0, 0);
    
    if (line1) {
        display.println(line1);
    }
    if (line2) {
        display.println(line2);
    }
    if (line3) {
        display.println(line3);
    }
    
    display.display();
}

uint8_t getCurrentPage() {
    return currentPage;
}
