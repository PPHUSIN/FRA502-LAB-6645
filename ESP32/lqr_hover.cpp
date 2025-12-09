#include "lqr_hover.h"

void LQR_Hover::Setpoint(float setpoint[9], float roll, float pitch, float yaw, float High) {
    for(int i=0; i<9; i++) setpoint[i] = 0.0f;
    
    setpoint[0] = roll;
    setpoint[1] = pitch;
    setpoint[2] = yaw;
    setpoint[7] = High; 
}

void LQR_Hover::LQR_Controller(float output_matrix[5], float setpoint[9], float measurment[9]) {
    float error[9] = {0};
    
    for (int i = 0; i < 9; i++) {
        error[i] = setpoint[i] - measurment[i];
    }

    for (int i = 0; i < 5; i++) {
        output_matrix[i] = 0.0f; 
        for (int j = 0; j < 9; j++) {
            output_matrix[i] += k_Hover[i][j] * error[j];
        }
    }
}