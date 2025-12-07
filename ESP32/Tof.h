#ifndef TOF_H
#define TOF_H
#include <Arduino.h>
#include <Adafruit_VL53L1X.h>

#define TOF_ADDRESS 0x29

void ToFinit();
float ReadAltitude();
#endif