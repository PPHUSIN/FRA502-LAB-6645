#ifndef DRONE_MODEL_H
#define DRONE_MODEL_H

#include <math.h>
#include <string.h>

// กำหนดขนาด Matrix (State 12, Input 5)
#define STATE_DIM 12
#define INPUT_DIM 5

// โครงสร้างสำหรับเก็บค่าคงที่ทางฟิสิกส์ (ต้องวัดค่าจริงมาใส่)
struct DroneParams {
    float m;        // Mass (kg) [cite: 480]
    float g;        // Gravity (9.81 m/s^2)
    float l;        // Distance COM to Fin pivot (m) [cite: 675]
    float r;        // Radius from center to Fin (m) [cite: 675]
    float Ixx;      // Inertia X (kg*m^2) [cite: 491]
    float Iyy;      // Inertia Y (kg*m^2)
    float Izz;      // Inertia Z (kg*m^2)
    
    // Aerodynamics Constants [cite: 637-640]
    float C_L_alpha; // Slope of lift coefficient
    float C_D_0;     // Drag coefficient bias
    float A_fin;     // Fin surface area (m^2)
    float A_duct;    // Duct cross-sectional area (m^2)
    
    // Motor Constants [cite: 548]
    float K_f;       // Motor thrust coefficient (Thrust = Kf * w^2)

    float K_f_matrix[12][6]; // Kalman Gain matrix
};

class DroneModel {
public:
    // Constructor
    DroneModel();

    // กำหนดค่า Parameters
    void setParams(DroneParams params);

    // คำนวณ Matrix A และ B (Continuous Time) ที่จุด Hover
    void computeContinuousModel(float hover_thrust_force, float hover_motor_speed);

    // แปลงเป็น Discrete Time สำหรับ Kalman Filter (Ad = I + A*dt)
    void discretize(float dt);

    // ตัวแปรเก็บ Matrix (Public เพื่อให้ดึงไปใช้กับ Kalman ได้ง่าย)
    float A[STATE_DIM][STATE_DIM]; // Continuous A
    float B[STATE_DIM][INPUT_DIM]; // Continuous B
    float Ad[STATE_DIM][STATE_DIM]; // Discrete A (สำหรับ EKF)e
    float Bd[STATE_DIM][INPUT_DIM]; // Discrete B (สำหรับ EKF)

    void predictState(float state[STATE_DIM], float input[INPUT_DIM], float new_state[STATE_DIM]);

    void updateStateWithMeasurements(float predict_state[STATE_DIM], float sensor_state[6], float new_state[STATE_DIM]);

private:
    DroneParams p;
    bool params_set;
};

#endif
