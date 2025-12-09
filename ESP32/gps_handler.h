#ifndef GPS_HANDLER_H
#define GPS_HANDLER_H

#include <Arduino.h>
#include <TinyGPS++.h>

struct GPSData {
    double latitude;
    double longitude;
    double altitude;
    double speed;
    int satellites;
    bool isValid;
};

void initGPS(int rxPin, int txPin, long baudRate = 9600);
void updateGPS();
void updateGPSWithDebug();
GPSData getGPSData();
void printGPSData();
void testGPSConnection();
int getGPSCharsProcessed();
void setGPSHint(double latitude, double longitude);
#endif