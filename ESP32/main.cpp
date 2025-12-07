// #include <Arduino.h>
// #include <Wire.h>
// #include <Adafruit_GFX.h>
// #include <Adafruit_SH110X.h>
// #include "imu.h"
// #include "led_status.h"
// #include "wifi_manager.h"
// #include "microros_handler.h"
// #include "gps_handler.h"
// #include "oled_display.h"
// // #include "Controller.h"
// #include "Tof.h"
// #include "Actuator.h"
// #include "kalman.h"
// #include "lqr_hover.h"
// // ============================================
// // DUAL CORE CONFIGURATION
// // ============================================
// #define CORE_IMU_CONTROL 0  // Core 0: High-priority real-time tasks
// #define CORE_COMM_UI 1      // Core 1: Communication & UI tasks

// // Task handles
// TaskHandle_t taskIMUHandle = NULL;
// TaskHandle_t taskROSHandle = NULL;
// TaskHandle_t taskGPSHandle = NULL;
// TaskHandle_t taskDisplayHandle = NULL;

// // Mutex for shared resources
// SemaphoreHandle_t i2cMutex;
// SemaphoreHandle_t dataMutex;

// ROVController rov;

// // WiFi credentials
// char WIFI_SSID[] = "iPhone";
// char WIFI_PASSWORD[] = "phu27816234";

// // micro-ROS configuration
// MicroROSConfig ros_config = {
//     .agent_ip = (char*)"172.20.10.2",
//     .agent_port = 8888,
//     .node_name = (char*)"esp32_node",
//     .topic_name = (char*)"esp32_s3_Drone",
//     .domain_id = 42,
//     .timer_timeout_ms = 10
// };

// // GPS Configuration
// #define GPS_RX_PIN 17
// #define GPS_TX_PIN 18
// #define GPS_BAUD 9600

// // I2C Configuration
// #define I2C_SDA 8
// #define I2C_SCL 9

// // Global instances
// MPU9250_IMU imu;
// DroneModel Tewadon;
// DroneParams p; 
// // ThrustVectorController ctrl(&imu);  // Pass IMU pointer to controller
// // LQRController ctrl(&imu);

// // Connection states
// volatile bool wifi_connected = false;
// volatile bool agent_connected = false;

// extern uint8_t currentPage;

// float Altitude = 0.0;

// unsigned long last_time = 0;
// float state_est[STATE_DIM];    
// float state_pred[STATE_DIM];   
// float control_input[5];
// float measurement[6];

// // ตัวแปรสำหรับ LQR
// float Setpoint[9];
// float measurement_LQR[9];
// float control_output[5];
// void filter(){
//     measurement[0] = imu.getRoll() * (PI/180.0f);
//     measurement[1] = imu.getPitch() * (PI/180.0f);
//     measurement[2] = imu.getYaw() * (PI/180.0f); 
//     measurement[3] = 0.0;
//     measurement[4] = 0.0;
//     measurement[5] = 0.0;
//     float sim_rpm_for_model = (control_input[4] > 200.0f) ? control_input[4] : 200.0f;
//     Tewadon.computeContinuousModel(p.m * p.g, sim_rpm_for_model); 
//     Tewadon.discretize(0.01);
//     Tewadon.predictState(state_est, control_input, state_pred);
//     Tewadon.updateStateWithMeasurements(state_pred, measurement, state_est);
// }
// // ============================================
// // CORE 0: IMU & CONTROL TASK (Real-time Critical)
// // Priority: 3 (Highest)
// // Frequency: 100Hz
// // ============================================
// void taskIMUControl(void *parameter) {
//     Serial.println("🔥 Core 0: IMU & Control task started");
//     TickType_t xLastWakeTime = xTaskGetTickCount();
//     const TickType_t xFrequency = pdMS_TO_TICKS(10); // 100Hz
    
//     while(1) {
//         // Critical: IMU reading with I2C mutex
//         if (xSemaphoreTake(i2cMutex, pdMS_TO_TICKS(5)) == pdTRUE) {
//             imu.readSensorData();      // อ่านและแปลงแกนอัตโนมัติ
//             imu.calculateOrientation(); // คำนวณ Roll, Pitch, Yaw
//             // Altitude = ReadAltitude();
//             filter();
//             Altitude = 0;
//             xSemaphoreGive(i2cMutex);
//         }
        
//         // Debug print (ลดความถี่ลงเพื่อไม่ให้ล้น Serial)
//         static unsigned long lastPrint = 0;
//         if (millis() - lastPrint >= 100) {  // Print every 100ms
//             Serial.printf("Roll: %.1f  Pitch: %.1f  Yaw: %.1f\n", 
//                       imu.getRoll(),imu.getPitch(), imu.getMagYaw());
//             // Serial.printf("Roll: %.1f  Pitch: %.1f  Yaw: %.1f\n Alt: %.3f\n", 
//             //           state_est[0]* (180.0f/PI), state_est[1]* (180.0f/PI), state_est[2]* (180.0f/PI),Altitude);
//             // Serial.printf("Alt: %.3f\n",Altitude);
//             lastPrint = millis();
//         }
        
//         // PID Control & Servo (no I2C needed)
//         // ctrl.update();
//         rov.update();

//         // Maintain precise 100Hz timing
//         vTaskDelayUntil(&xLastWakeTime, xFrequency);
//     }
// }

// // ============================================
// // CORE 1: MICRO-ROS TASK (Communication)
// // Priority: 2 (High)
// // Frequency: As fast as possible
// // ============================================
// void taskMicroROS(void *parameter) {
//     Serial.println("📡 Core 1: micro-ROS task started");
    
//     while(1) {
//         if (wifi_connected) {
//             runMicroROS();
//             stopPublishing();
//             if (xSemaphoreTake(dataMutex, pdMS_TO_TICKS(2)) == pdTRUE) {
//                 agent_connected = isAgentConnected();
//                 xSemaphoreGive(dataMutex);
//             }
            
//             updateStatusLED(wifi_connected, agent_connected, false);
//         } else {
//             vTaskDelay(pdMS_TO_TICKS(100));
//         }
        
//         vTaskDelay(pdMS_TO_TICKS(1)); // Minimal delay for task switching
//     }
// }

// // ============================================
// // CORE 1: GPS TASK (Serial Communication)
// // Priority: 2 (High)
// // Frequency: 10ms
// // ============================================
// void taskGPS(void *parameter) {
//     Serial.println("🛰️ Core 1: GPS task started");
//     TickType_t xLastWakeTime = xTaskGetTickCount();
//     const TickType_t xFrequency = pdMS_TO_TICKS(10);
    
//     unsigned long lastPrint = 0;
    
//     while(1) {
//         GPSData gpsData = getGPSData();
        
//         // Print every 1 second
//         if (millis() - lastPrint >= 1000) {
//             if (gpsData.isValid) {
//                 Serial.println("✓ GPS has valid fix!");
//                 // REMOVED: Distance calculation from WiFi Pos
//             }
//             lastPrint = millis();
//         }
        
//         vTaskDelayUntil(&xLastWakeTime, xFrequency);
//     }
// }

// // ============================================
// // CORE 1: DISPLAY TASK (I2C Communication)
// // Priority: 1 (Normal)
// // Frequency: 500ms
// // ============================================
// void taskDisplay(void *parameter) {
//     Serial.println("📺 Core 1: Display task started");
//     TickType_t xLastWakeTime = xTaskGetTickCount();
//     const TickType_t xFrequency = pdMS_TO_TICKS(500);
    
//     unsigned long lastPageSwitch = 0;
//     const unsigned long PAGE_SWITCH_INTERVAL = 5000;
    
//     while(1) {
//         // Auto switch page
//         if (millis() - lastPageSwitch >= PAGE_SWITCH_INTERVAL) {
//             switchDisplayPage();
//             lastPageSwitch = millis();
//         }
        
//         // Update display with I2C mutex
//         if (xSemaphoreTake(i2cMutex, pdMS_TO_TICKS(20)) == pdTRUE) {
//             GPSData gpsData = getGPSData();
            
//             switch(currentPage) {
//                 case 0:
//                     displayGPSPage();
//                     break;
//                 case 1:
//                     displayWiFiPage(WIFI_SSID, wifi_connected, agent_connected);
//                     break;
//                 case 2:
//                     // MODIFIED: เดิมคือ displayPositionPage(wifiPos, gpsData);
//                     // เปลี่ยนเป็นแสดงหน้า GPS แทนเนื่องจากไม่มี wifiPos แล้ว
//                     displayGPSPage(); 
//                     break;
//             }
            
//             xSemaphoreGive(i2cMutex);
//         }
        
//         vTaskDelayUntil(&xLastWakeTime, xFrequency);
//     }
// }
// void enableDLPF() {
//     Wire.beginTransmission(0x68);
//     Wire.write(0x1A); 
//     Wire.write(0x05); 
//     Wire.endTransmission();
//     Serial.println("DLPF Enabled");
// }

// void setupDroneParams() {
//     p.m = 0.7f;         
//     p.g = 9.81f;

//     p.l = 0.048f;
//     p.r = 0.029f;
//     p.Ixx = 0.01f;
//     p.Iyy = 0.01f;
//     p.Izz = 0.02f;
    
//     // Aerodynamics
//     p.C_L_alpha = 0.108f; 
//     p.C_D_0 = 0.01f;
//     p.A_fin = 0.0028f;
//     p.A_duct = 0.0038f;
    
//     // Motor
//     p.K_f = 1.05e-6f;

//     memset(p.K_f_matrix, 0, sizeof(p.K_f_matrix));

//     float gain_gyro = 0.02f;

//     p.K_f_matrix[0][0] = 0.005; 
//     p.K_f_matrix[1][1] = 0.005; 
//     p.K_f_matrix[2][2] = 0.02f; 
//     p.K_f_matrix[3][3] = gain_gyro; 
//     p.K_f_matrix[4][4] = gain_gyro; 
//     p.K_f_matrix[5][5] = gain_gyro;

//     Tewadon.setParams(p);
// }
// // ============================================
// // SETUP (Runs on Core 1)
// // ============================================
// void setup() {
//     Serial.begin(115200);
//     delay(2000);
    
//     // Create mutexes FIRST
//     i2cMutex = xSemaphoreCreateMutex();
//     dataMutex = xSemaphoreCreateMutex();
    
//     if (i2cMutex == NULL || dataMutex == NULL) {
//         Serial.println("❌ Failed to create mutexes!");
//         ESP.restart();
//     }
    
//     // Initialize I2C
//     Serial.println("\n=== Initializing I2C Bus ===");
//     Wire.begin(I2C_SDA, I2C_SCL);
//     Wire.setClock(400000);
//     Wire.setTimeout(100);
//     Serial.println("✅ I2C Bus initialized (SDA=8, SCL=9)");
//     delay(100);

//     // Initialize IMU
//     Serial.println("\n=== Initializing IMU ===");
//     if (!imu.begin()) {
//         Serial.println("❌ IMU initialization failed!");
//         Serial.println("Continuing without IMU...");
//     } else {
//         Serial.println("✅ IMU initialized successfully");
        
//         // ⚙️ ตั้งค่า IMU Rotation (เปลี่ยนได้ตรงนี้)
//         // imu.setRotation(ROTATION_CUSTOM_3);
//         imu.zeroOrientation();
        
//         // // 🧪 ทดสอบ IMU Rotation (Comment out หลังทดสอบเสร็จ)
//         // Serial.println("\n⏳ Waiting 3 seconds before IMU test...");
//         // delay(3000);
//         // imu.printOrientation();  // แสดงคำแนะนำ
//         // delay(2000);
//         // imu.testRotation(30);    // ทดสอบ 30 ตัวอย่าง (3 วินาที)
//         // Serial.println("✓ IMU test complete! Continuing setup...\n");
//         // delay(2000);
//     }
//     setupDroneParams();
//     memset(state_est, 0, sizeof(state_est));
//     last_time = micros();
//     enableDLPF(); 
//     delay(100);
//     // ToFinit();
//     delay(100);
//     // Initialize Controller
//     Serial.println("\n=== Initializing Controller ===");
//     // ctrl.begin();
//     delay(100);
    
//     // Initialize OLED
//     Serial.println("\n=== Initializing OLED Display ===");
//     initDisplay(); 
//     initLED();
    
//     Serial.println("\n🚀 ESP32-S3 Dual Core Configuration");
//     Serial.println("Core 0: IMU (100Hz) + Control");
//     Serial.println("Core 1: ROS + GPS + Display");
//     Serial.println();

//     // Initialize GPS
//     Serial.println("Initializing GPS...");
//     initGPS(GPS_RX_PIN, GPS_TX_PIN, GPS_BAUD);
    
//     // Connect WiFi
//     showMessage("Connecting WiFi...");
//     wifi_connected = initWiFi(WIFI_SSID, WIFI_PASSWORD);
//     if (!wifi_connected) {
//         Serial.println("WiFi connection failed! Restarting...");
//         showMessage("WiFi FAILED!", "Restarting...");
//         delay(2000);
//         ESP.restart();
//     }
    
    
//     // Initialize micro-ROS
//     showMessage("WiFi Connected!", "Connecting ROS...");
//     agent_connected = initMicroROS(WIFI_SSID, WIFI_PASSWORD, ros_config);
//     if (!agent_connected) {
//         Serial.println("micro-ROS initialization failed! Restarting...");
//         showMessage("ROS FAILED!", "Restarting...");
//         delay(2000);
//         ESP.restart();
//     }
        
//     Serial.println("\n=== Creating Tasks ===");
    
//     // CORE 0: IMU & Control (Highest Priority)
//     xTaskCreatePinnedToCore(
//         taskIMUControl,           // Task function
//         "IMU_Control",            // Task name
//         4096,                     // Stack size
//         NULL,                     // Parameters
//         3,                        // Priority (Highest)
//         &taskIMUHandle,           // Task handle
//         CORE_IMU_CONTROL          // Core 0
//     );
//     Serial.println("✅ Core 0: IMU & Control task created (Priority: 3)");
    
//     // CORE 1: micro-ROS (High Priority)
//     xTaskCreatePinnedToCore(
//         taskMicroROS,
//         "MicroROS",
//         8192,                     // Larger stack for ROS
//         NULL,
//         2,                        // Priority: High
//         &taskROSHandle,
//         CORE_COMM_UI              // Core 1
//     );
//     Serial.println("✅ Core 1: micro-ROS task created (Priority: 2)");
    
//     // CORE 1: GPS (High Priority)
//     xTaskCreatePinnedToCore(
//         taskGPS,
//         "GPS",
//         4096,
//         NULL,
//         2,                        // Priority: High
//         &taskGPSHandle,
//         CORE_COMM_UI              // Core 1
//     );
//     Serial.println("✅ Core 1: GPS task created (Priority: 2)");
    
//     // CORE 1: Display (Normal Priority)
//     xTaskCreatePinnedToCore(
//         taskDisplay,
//         "Display",
//         4096,
//         NULL,
//         1,                        // Priority: Normal
//         &taskDisplayHandle,
//         CORE_COMM_UI              // Core 1
//     );
//     Serial.println("✅ Core 1: Display task created (Priority: 1)");
    
//     rov.begin();
//     Serial.println("\n🎉 Setup complete! All tasks running.");
//     showMessage("Setup Complete!", "Tasks Running");
//     delay(2000);
// }

// // ============================================
// // LOOP (Runs on Core 1, but mostly idle now)
// // ============================================
// void loop() {
//     // Monitor WiFi connection (low priority background task)
//     static unsigned long lastWiFiCheck = 0;
//     if (millis() - lastWiFiCheck >= 5000) {
//         bool current_wifi_status = checkWiFiConnection();
        
//         if (current_wifi_status != wifi_connected) {
//             wifi_connected = current_wifi_status;
            
//             if (!wifi_connected) {
//                 agent_connected = false;
//                 reconnectWiFi(WIFI_SSID, WIFI_PASSWORD);
//                 wifi_connected = true;
//             }
//         }
        
//         lastWiFiCheck = millis();
//     }
    
//     // REMOVED: Loop update for WiFi Position
    
//     delay(1000); // Loop can be slow since all work is in tasks
// }