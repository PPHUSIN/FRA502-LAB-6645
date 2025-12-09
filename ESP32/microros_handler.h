#ifndef MICROROS_HANDLER_H
#define MICROROS_HANDLER_H

#include <Arduino.h>
#include <micro_ros_arduino.h>
#include <rcl/rcl.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>
#include <std_msgs/msg/int16.h>
#include <sensor_msgs/msg/nav_sat_fix.h>
struct MicroROSConfig {
    char* agent_ip;
    int agent_port;
    char* node_name;
    char* topic_name;
    int domain_id;
    unsigned int timer_timeout_ms;
};
void stopPublishing();
void startPublishing();
bool initMicroROS(char* ssid, char* password, MicroROSConfig config);
void runMicroROS();
bool isAgentConnected();
int16_t getCurrentMessageData();

#endif