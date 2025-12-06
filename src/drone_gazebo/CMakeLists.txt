cmake_minimum_required(VERSION 3.8)
project(drone_gazebo)

# Default compiler settings
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

# ==========================================================
# INSTALLATION RULES
# These commands copy your files from 'src' to 'install'
# so Gazebo and ROS 2 can actually find them.
# ==========================================================

# Install Python Module
ament_python_install_package(${PROJECT_NAME})

# Install Python executables
install(PROGRAMS
  scripts/dummy_script.py
  scripts/lqr_node.py
  scripts/lqr_hover_node.py
  scripts/tvc_controller.py
  scripts/origin_return_diagnostic.py
  DESTINATION lib/${PROJECT_NAME}
)

# Include Cpp "include" directory
include_directories(include)

# 1. Install Launch Files
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

# 2. Install URDF Files
install(DIRECTORY urdf
  DESTINATION share/${PROJECT_NAME}
)

# 3. Install Mesh Components
# Your URDF uses "component", so we install that folder.
install(DIRECTORY component
  DESTINATION share/${PROJECT_NAME}
)

# 4. Install World Files (Optional)
# If you created a 'worlds' folder, uncomment the lines below:
# install(DIRECTORY worlds
#   DESTINATION share/${PROJECT_NAME}
# )

ament_package()
