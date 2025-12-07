#ifndef OLED_DISPLAY_H
#define OLED_DISPLAY_H
#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>
#include "gps_handler.h"
#include "imu.h"
#define OLED_SDA 8
#define OLED_SCL 9
// OLED pins - using different pins from IMU
#define OLED_RESET -1

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define SCREEN_ADDRESS 0x3C

extern uint8_t currentPage;
extern const uint8_t MAX_PAGES;
void initDisplay();
void showMessage(const char* line1, const char* line2 = "", const char* line3 = "");
void displayGPSPage();
void displayWiFiPage(const char* ssid, bool wifiConnected, bool agentConnected);
void displayPositionPage(GPSData gpsData);
void displayIMUPage(MPU9250_IMU& imu);  // เปลี่ยนเป็นรับ reference
void switchDisplayPage();

#endif