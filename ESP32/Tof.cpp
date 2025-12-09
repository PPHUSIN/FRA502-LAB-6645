#include "Tof.h"

// Define the sensor instance
Adafruit_VL53L1X lox = Adafruit_VL53L1X();

void ToFinit(){
    // Ensure Wire is already started in main setup before calling this
    if (!lox.begin()) {
        Serial.println(F("Failed to boot VL53L1X"));
        // Do not use while(1) here, it freezes the whole drone if sensor fails.
        // Just return, and handle the error in the main loop or status LED.
        return; 
    }
    
    // Set to Short range for faster, more accurate indoor/drone height (up to 1.3m)
    // Use VL53L1X_DISTANCE_MODE_LONG for outdoors (up to 4m)
    lox.startRanging(); 
    lox.setTimingBudget(50); // Set to 50ms for faster updates (default is usually slower)
}

float ReadAltitude(){
    static float output = 0.0;
    
    // This function MUST be called inside an I2C Mutex
    if (lox.dataReady()) {
        int16_t distance = lox.distance();
        
        if (distance != -1) {
            // Convert mm to meters (Float division)
            output = distance / 1000.0;
        }
        
        // Critical: Clear interrupt to get new data next time
        lox.clearInterrupt();
    }
    
    return output;
}