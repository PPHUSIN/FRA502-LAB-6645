#ifndef WIFI_MANAGER_H
#define WIFI_MANAGER_H

#include <Arduino.h>
#include <WiFi.h>

bool initWiFi(const char* ssid, const char* password);
bool checkWiFiConnection();
bool reconnectWiFi(const char* ssid, const char* password);

#endif