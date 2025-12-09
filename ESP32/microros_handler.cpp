#include "microros_handler.h"
#include "wifi_manager.h"
#include "led_status.h"
#include "gps_handler.h"
// micro-ROS objects
static rcl_node_t node;
static rclc_support_t support;
static rclc_executor_t executor;
static rcl_publisher_t publisher;
static rcl_timer_t timer;
static sensor_msgs__msg__NavSatFix Pungapond;
static std_msgs__msg__Int16 msg;
static rcl_allocator_t allocator;

static bool agent_connected = false;
static bool publishing_active = false;
static bool publishing_enabled = true;
void timer_callback(rcl_timer_t *timer, int64_t last_call_time) {
    (void)last_call_time;
    Pungapond.altitude = 15;

    if (!publishing_enabled) return;  // เพิ่มบรรทัดนี้
    
    // rcl_ret_t ret = rcl_publish(&publisher, &msg, NULL);
    rcl_ret_t Gps = rcl_publish(&publisher,&Pungapond,NULL);
    if (Gps == RCL_RET_OK) {
        Serial.print("Published: ");
        Serial.println(Pungapond.altitude);
        publishing_active = true;
        agent_connected = true;
    } else {
        Serial.println("Failed to publish message");
        agent_connected = false;
    }
}

bool initMicroROS(char* ssid, char* password, MicroROSConfig config) {
    // Configure micro-ROS transport
    set_microros_wifi_transports(ssid, password, config.agent_ip, config.agent_port);
    allocator = rcl_get_default_allocator();
    
    Serial.println("Connecting to micro-ROS agent...");
    setLEDAgentConnecting();
    
    // Domain ID configuration
    rcl_init_options_t init_options = rcl_get_zero_initialized_init_options();
    rcl_init_options_init(&init_options, allocator);
    rcl_init_options_set_domain_id(&init_options, config.domain_id);
    
    // Connect to agent with retry
    rcl_ret_t ret;
    int agent_attempts = 0;
    
    do {
        // Check WiFi status
        if (!checkWiFiConnection()) {
            Serial.println("WiFi lost during agent connection");
            setLEDReconnecting();
            
            if (!reconnectWiFi(ssid, password)) {
                return false;
            }
        }
        
        ret = rclc_support_init_with_options(&support, 0, NULL, &init_options, &allocator);
        if (ret != RCL_RET_OK) {
            Serial.println("Retrying agent connection...");
            blinkLED(COLOR_BLUE, 2, 250);
            
            agent_attempts++;
            if (agent_attempts > 30) {
                Serial.println("Agent connection timeout!");
                setLEDDisconnected();
                rcl_init_options_fini(&init_options);
                return false;
            }
        }
    } while (ret != RCL_RET_OK);
    
    Serial.println("Connected to micro-ROS agent!");
    agent_connected = true;
    setLEDBothConnected();
    delay(3000);
    
    // Clean up init options
    rcl_init_options_fini(&init_options);
    
    // Initialize ROS components
    rclc_node_init_default(&node, config.node_name, "", &support);
    rclc_publisher_init_default(&publisher, &node, 
                                ROSIDL_GET_MSG_TYPE_SUPPORT(sensor_msgs, msg, NavSatFix), 
                                config.topic_name);
    
    Pungapond.altitude = 0;
    Pungapond.latitude = 0;
    Pungapond.longitude = 0;


    
    rclc_timer_init_default(&timer, &support, 
                           RCL_MS_TO_NS(config.timer_timeout_ms), 
                           timer_callback);
    
    rclc_executor_init(&executor, &support.context, 1, &allocator);
    rclc_executor_add_timer(&executor, &timer);
    
    Serial.println("Setup complete! Ready to publish");
    setLEDBothConnected();
    
    return true;
}

void runMicroROS() {
    // msg.data++;
    Pungapond.altitude =  getGPSData().altitude;
    Pungapond.latitude =  getGPSData().latitude;
    Pungapond.longitude = getGPSData().longitude;
    rcl_ret_t ret = rclc_executor_spin_some(&executor, RCL_MS_TO_NS(100));
    
    // Monitor agent connection through executor return
    if (ret == RCL_RET_OK && !agent_connected) {
        agent_connected = true;
        Serial.println("Agent reconnected!");
    } else if (ret != RCL_RET_OK && agent_connected) {
        agent_connected = false;
        Serial.println("Agent connection lost!");
    }
    
    publishing_active = false;
}

bool isAgentConnected() {
    return agent_connected;
}

int16_t getCurrentMessageData() {
    return Pungapond.altitude;
}

void stopPublishing() {
    publishing_enabled = false;
    // Serial.println("Publishing stopped");
}

void startPublishing() {
    publishing_enabled = true;
    // Serial.println("Publishing started");
}