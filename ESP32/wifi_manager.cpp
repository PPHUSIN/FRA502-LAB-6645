#include "wifi_manager.h"
#include "led_status.h"

bool initWiFi(const char* ssid, const char* password) {
    Serial.print("Connecting to WiFi");
    setLEDWiFiConnecting();
    
    WiFi.begin(ssid, password);
    
    int wifi_attempt = 0;
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
        
        // Blink yellow while connecting
        if (wifi_attempt % 2 == 0) {
            setLEDWiFiConnecting();
        } else {
            setLED(COLOR_OFF);
        }
        wifi_attempt++;
        
        // Timeout after 30 seconds
        if (wifi_attempt > 60) {
            Serial.println("\nWiFi connection timeout!");
            setLEDDisconnected();
            return false;
        }
    }
    
    Serial.println();
    Serial.print("WiFi Connected! IP: ");
    Serial.println(WiFi.localIP());
    setLEDWiFiConnected();
    delay(2000);
    
    return true;
}

bool checkWiFiConnection() {
    return (WiFi.status() == WL_CONNECTED);
}

bool reconnectWiFi(const char* ssid, const char* password) {
    Serial.println("WiFi disconnected! Reconnecting...");
    setLEDReconnecting();
    
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
        blinkLED(COLOR_ORANGE, 1, 100);
    }
    
    Serial.println("\nWiFi reconnected!");
    setLEDWiFiConnected();
    delay(1000);
    
    return true;
}