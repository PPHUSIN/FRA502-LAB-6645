#include "led_status.h"

// Built-in RGB LED on ESP32-S3-N16R8
#define RGB_LED_PIN 48
#define NUM_PIXELS 1

Adafruit_NeoPixel rgb_led(NUM_PIXELS, RGB_LED_PIN, NEO_GRB + NEO_KHZ800);

// LED Colors (initialized after rgb_led)
uint32_t COLOR_OFF;
uint32_t COLOR_RED;
uint32_t COLOR_YELLOW;
uint32_t COLOR_GREEN;
uint32_t COLOR_BLUE;
uint32_t COLOR_PURPLE;
uint32_t COLOR_WHITE;
uint32_t COLOR_ORANGE;

void initLED() {
    rgb_led.begin();
    rgb_led.setBrightness(5);
    rgb_led.clear();
    
    // Initialize colors
    COLOR_OFF = rgb_led.Color(0, 0, 0);
    COLOR_RED = rgb_led.Color(255, 0, 0);
    COLOR_YELLOW = rgb_led.Color(255, 255, 0);
    COLOR_GREEN = rgb_led.Color(0, 255, 0);
    COLOR_BLUE = rgb_led.Color(0, 0, 255);
    COLOR_PURPLE = rgb_led.Color(128, 0, 128);
    COLOR_WHITE = rgb_led.Color(255, 255, 255);
    COLOR_ORANGE = rgb_led.Color(255, 165, 0);
    
    setLED(COLOR_RED); // Start with red (disconnected)
}

void setLED(uint32_t color) {
    rgb_led.setPixelColor(0, color);
    rgb_led.show();
}

void updateStatusLED(bool wifi_connected, bool agent_connected, bool publishing) {
    if (publishing && wifi_connected && agent_connected) {
        setLED(COLOR_PURPLE);
    } else if (wifi_connected && agent_connected) {
        setLED(COLOR_PURPLE);
    } else if (wifi_connected && !agent_connected) {
        setLED(COLOR_GREEN);
    } else if (!wifi_connected) {
        setLED(COLOR_RED);
    }
}

void blinkLED(uint32_t color, int blinks, int duration) {
    for (int i = 0; i < blinks; i++) {
        setLED(color);
        delay(duration);
        setLED(COLOR_OFF);
        delay(duration);
    }
}

// Helper functions
void setLEDDisconnected() {
    setLED(COLOR_RED);
}

void setLEDWiFiConnecting() {
    setLED(COLOR_YELLOW);
}

void setLEDWiFiConnected() {
    setLED(COLOR_GREEN);
}

void setLEDAgentConnecting() {
    setLED(COLOR_BLUE);
}

void setLEDBothConnected() {
    setLED(COLOR_PURPLE);
}

void setLEDReconnecting() {
    setLED(COLOR_ORANGE);
}