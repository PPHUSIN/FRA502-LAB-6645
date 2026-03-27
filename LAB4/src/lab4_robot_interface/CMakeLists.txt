cmake_minimum_required(VERSION 3.5)
project(lab4_robot_interface)

# 1. Find Dependencies ที่จำเป็นสำหรับการสร้าง msg/srv
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(geometry_msgs REQUIRED) # ต้องมีเพราะ srv ใช้ geometry_msgs/Pose

# 2. สั่ง Generate Code (หัวใจสำคัญ)
rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/GetTarget.srv"
  "srv/SetRobotMode.srv"
  DEPENDENCIES geometry_msgs
)

# 3. Export dependency ให้ package อื่นเรียกใช้ได้
ament_export_dependencies(rosidl_default_runtime)

ament_package()