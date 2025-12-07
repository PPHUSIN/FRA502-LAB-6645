#ifndef LED_STATUS_H
#define LED_STATUS_H

#include <Arduino.h>
#include <Adafruit_NeoPixel.h>

// LED Colors
extern uint32_t COLOR_OFF;
extern uint32_t COLOR_RED;
extern uint32_t COLOR_YELLOW;
extern uint32_t COLOR_GREEN;
extern uint32_t COLOR_BLUE;
extern uint32_t COLOR_PURPLE;
extern uint32_t COLOR_WHITE;
extern uint32_t COLOR_ORANGE;

void initLED();
void setLED(uint32_t color);
void updateStatusLED(bool wifi_connected, bool agent_connected, bool publishing);
void blinkLED(uint32_t color, int blinks, int duration = 200);

// Helper functions for specific states
void setLEDDisconnected();
void setLEDWiFiConnecting();
void setLEDWiFiConnected();
void setLEDAgentConnecting();
void setLEDBothConnected();
void setLEDReconnecting();

#endif