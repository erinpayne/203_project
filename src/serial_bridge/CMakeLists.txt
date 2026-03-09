cmake_minimum_required(VERSION 3.8)
project(serial_bridge)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)

# Install Python packages
ament_python_install_package(${PROJECT_NAME})

# Install Python executables
install(PROGRAMS
  ${PROJECT_NAME}/serial_bridge_node.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME serial_bridge_node
)

# Install launch files
install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})

ament_package()
