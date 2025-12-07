#include "kalman.h"

DroneModel::DroneModel() {
    params_set = false;
    // เคลียร์ค่า Matrix เป็น 0 เริ่มต้น
    memset(A, 0, sizeof(A));
    memset(B, 0, sizeof(B));
    memset(Ad, 0, sizeof(Ad));
    memset(Bd, 0, sizeof(Bd));
}

void DroneModel::setParams(DroneParams params) {
    this->p = params;
    this->params_set = true;
}

void DroneModel::computeContinuousModel(float F_t, float w_0) {
    if (!params_set) return;

    // เคลียร์ Matrix ก่อนคำนวณใหม่
    memset(A, 0, sizeof(A));
    memset(B, 0, sizeof(B));

    // --- คำนวณค่าสัมประสิทธิ์รวม (Lumped Coefficients) ---
    // สูตรจาก Eq 3.16: Force = Ft * (CL_alpha * Afin / 2*Aduct) * alpha
    // เราเรียกเทอมในวงเล็บว่า K_aero (Aerodynamic Gain)
    float K_aero = (p.C_L_alpha * p.A_fin) / (2.0f * p.A_duct);
    
    // แรง Lift ต่อ 1 องศาของ Fin ที่จุด Hover (N/rad)
    float F_per_rad = F_t * K_aero; 

    // --- สร้าง Matrix A (System Matrix) ---
    // อ้างอิง Eq 3.42 [cite: 861]
    // State Vector x: [phi, theta, psi, wx, wy, wz, x, y, z, vx, vy, vz]
    
    // 1. ความสัมพันธ์ Kinematics (dot_angle = angular_velocity)
    A[0][3] = 1.0f; // d(phi) = wx
    A[1][4] = 1.0f; // d(theta) = wy
    A[2][5] = 1.0f; // d(psi) = wz

    // 2. ความสัมพันธ์ Position (dot_pos = velocity)
    A[6][9] = 1.0f; // dx = vx
    A[7][10] = 1.0f; // dy = vy
    A[8][11] = 1.0f; // dz = vz

    // 3. ความสัมพันธ์ Velocity (Gravity terms) จาก Eq 3.41 [cite: 856]
    // dot_vx = ... - g * theta
    A[9][1] = -p.g; 
    // dot_vy = ... + g * phi
    A[10][0] = p.g;
    
    // --- สร้าง Matrix B (Input Matrix) ---
    // อ้างอิง Eq 3.43 [cite: 881]
    // Input Vector u: [alpha1, alpha2, alpha3, alpha4, w_motor]

    // เทอม Torque (Angular Acceleration)
    // dot_wx = (l / Ixx) * (F1 + F3) -> Alpha 1, 3
    float term_wx = (p.l * F_per_rad) / p.Ixx;
    B[3][0] = term_wx; // alpha1
    B[3][2] = term_wx; // alpha3

    // dot_wy = (l / Iyy) * (F2 + F4) -> Alpha 2, 4
    float term_wy = (p.l * F_per_rad) / p.Iyy;
    B[4][1] = term_wy; // alpha2
    B[4][3] = term_wy; // alpha4

    // dot_wz = (r / Izz) * (F1 - F2 - F3 + F4) -> Alpha 1,2,3,4
    float term_wz = (p.r * F_per_rad) / p.Izz;
    B[5][0] =  term_wz; // alpha1
    B[5][1] = -term_wz; // alpha2
    B[5][2] = -term_wz; // alpha3
    B[5][3] =  term_wz; // alpha4

    // เทอม Linear Acceleration (Force/Mass)
    // dot_vx = (F2 + F4) / m
    float term_vx = F_per_rad / p.m;
    B[9][1] = term_vx; // alpha2
    B[9][3] = term_vx; // alpha4

    // dot_vy = (F1 + F3) / m
    float term_vy = F_per_rad / p.m;
    B[10][0] = term_vy; // alpha1
    B[10][2] = term_vy; // alpha3

    // dot_vz (Motor Thrust) จาก Eq 3.41 ตัวสุดท้าย
    // dot_vz = (2 * Kf * w0 * (1-Cd)) / m
    // หมายเหตุ: ใช้ w_0 คือความเร็วรอบขณะ hover
    float term_vz = (2.0f * p.K_f * w_0 * (1.0f - p.C_D_0)) / p.m;
    B[11][4] = term_vz; // motor_omega input
}

void DroneModel::discretize(float dt) {
    // ใช้ Euler Discretization อย่างง่าย: 
    // Ad = I + A * dt
    // Bd = B * dt
    // (สำหรับ Kalman Filter บน MCU วิธีนี้เร็วและเพียงพอสำหรับ Loop rate สูงๆ เช่น >100Hz)

    // 1. คำนวณ Ad
    for(int i=0; i<STATE_DIM; i++) {
        for(int j=0; j<STATE_DIM; j++) {
            Ad[i][j] = A[i][j] * dt;
            if(i == j) {
                Ad[i][j] += 1.0f; // บวก Identity Matrix
            }
        }
    }

    // 2. คำนวณ Bd
    for(int i=0; i<STATE_DIM; i++) {
        for(int j=0; j<INPUT_DIM; j++) {
            Bd[i][j] = B[i][j] * dt;
        }
    }
}

void DroneModel::predictState(float state[STATE_DIM], float input[INPUT_DIM], float new_state[STATE_DIM]) {
    // คำนวณสถานะถัดไป: new_state = Ad * state + Bd * input
    float temp_state[STATE_DIM] = {0};

    // คำนวณ Ad * state
    for(int i=0; i<STATE_DIM; i++) {
        for(int j=0; j<STATE_DIM; j++) {
            temp_state[i] += Ad[i][j] * state[j];
        }
    }

    // บวก Bd * input
    for(int i=0; i<STATE_DIM; i++) {
        for(int j=0; j<INPUT_DIM; j++) {
            temp_state[i] += Bd[i][j] * input[j];
        }
    }

    // คัดลอกผลลัพธ์ไปยัง new_state
    memcpy(new_state, temp_state, sizeof(float) * STATE_DIM);
}

void DroneModel::updateStateWithMeasurements(float predict_state[STATE_DIM], float sensor_state[6], float updated_state[STATE_DIM]) {
    // x = x_predict + K * (y - H*x_predict)
    
    float temp_state[STATE_DIM] = {0};

    float y_minus_Hx[6] = {0};

    float correction[STATE_DIM] = {0};

    for (int i = 0; i < 6; i++) {
        y_minus_Hx[i] = sensor_state[i] - predict_state[i];
    }

    for (int i = 0; i < STATE_DIM; i++) {
        for (int j = 0; j < 6; j++) {
            correction[i] += p.K_f_matrix[i][j] * y_minus_Hx[j];
        }
    }

    for (int i = 0; i < STATE_DIM; i++) {
        temp_state[i] = predict_state[i] + correction[i];
    }

    memcpy(updated_state, temp_state, sizeof(float) * STATE_DIM);
}