#!/usr/bin/env python3
# pyright: ignore[reportMissingImports]

import serial
import time
import math
import threading
from typing import Optional

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped
import tf_transformations


class SerialBridgeNode(Node):
    """
    ROS2 node for communicating with Arduino motor controller.
    
    Publishes: odometry, tf transforms
    Subscribes: cmd_vel (Twist messages)
    """
    
    def __init__(self):
        super().__init__('serial_bridge')
        
        # Declare parameters
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('wheel_radius', 0.05)  # meters
        self.declare_parameter('wheel_separation', 0.2)  # meters
        self.declare_parameter('encoder_cpr', 600)  # counts per revolution
        self.declare_parameter('publish_rate', 50)  # Hz
        
        # Get parameters
        self.port = self.get_parameter('port').value
        self.baudrate = self.get_parameter('baudrate').value
        self.wheel_radius = self.get_parameter('wheel_radius').value
        self.wheel_separation = self.get_parameter('wheel_separation').value
        self.encoder_cpr = self.get_parameter('encoder_cpr').value
        publish_rate = self.get_parameter('publish_rate').value
        
        # Serial communication
        self.ser: Optional[serial.Serial] = None
        self.serial_lock = threading.Lock()
        
        # Odometry tracking
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.left_encoder_last = 0
        self.right_encoder_last = 0
        self.last_time = self.get_clock().now()
        
        # Publishers and broadcasters
        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # Subscribers
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            'cmd_vel',
            self.cmd_vel_callback,
            10
        )
        
        # Timer for publishing odometry
        self.create_timer(1.0 / publish_rate, self.publish_odometry)
        
        # Initialize serial connection
        self.connect_serial()
        
        self.get_logger().info(f'Serial bridge initialized on {self.port} @ {self.baudrate} baud')
    
    def connect_serial(self):
        """Establish serial connection with Arduino."""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1.0
            )
            time.sleep(2)  # Wait for Arduino to reset
            self.get_logger().info('Serial connection established')
        except serial.SerialException as e:
            self.get_logger().error(f'Failed to connect to serial port: {e}')
    
    def send_motor_command(self, left_speed: float, right_speed: float):
        """
        Send motor command to Arduino.
        
        Format: "L<speed>,R<speed>\n"
        Speeds range from -255 to 255
        """
        # Constrain speeds
        left_speed = max(-255, min(255, int(left_speed)))
        right_speed = max(-255, min(255, int(right_speed)))
        
        command = f"L{left_speed},R{right_speed}\n"
        
        if self.ser and self.ser.is_open:
            with self.serial_lock:
                try:
                    self.ser.write(command.encode())
                except serial.SerialException as e:
                    self.get_logger().error(f'Serial write error: {e}')
    
    def read_encoder_data(self) -> tuple:
        """
        Read encoder data from Arduino.
        
        Format: "E<left>,<right>\n"
        Returns: (left_encoder, right_encoder) or (None, None) on error
        """
        if self.ser and self.ser.is_open:
            with self.serial_lock:
                try:
                    if self.ser.in_waiting:
                        line = self.ser.readline().decode('utf-8').strip()
                        if line.startswith('E'):
                            parts = line[1:].split(',')
                            if len(parts) == 2:
                                left = int(parts[0])
                                right = int(parts[1])
                                return left, right
                except (serial.SerialException, ValueError, UnicodeDecodeError) as e:
                    self.get_logger().warn(f'Serial read error: {e}')
        
        return None, None
    
    def cmd_vel_callback(self, msg: Twist):
        """
        Process velocity command and send to motors.
        
        Converts Twist (linear.x and angular.z) to left/right wheel speeds.
        """
        # Extract linear and angular velocity
        v = msg.linear.x  # forward speed (m/s)
        w = msg.angular.z  # angular speed (rad/s)
        
        # Differential drive kinematics
        # v_left = v - (w * wheel_separation / 2)
        # v_right = v + (w * wheel_separation / 2)
        v_left = v - (w * self.wheel_separation / 2.0)
        v_right = v + (w * self.wheel_separation / 2.0)
        
        # Convert linear velocity to motor command (0-255)
        # Assuming max speed is 1 m/s
        max_speed = 1.0
        left_cmd = (v_left / max_speed) * 255
        right_cmd = (v_right / max_speed) * 255
        
        self.send_motor_command(left_cmd, right_cmd)
    
    def publish_odometry(self):
        """Read encoders and publish odometry."""
        left_count, right_count = self.read_encoder_data()
        
        if left_count is None or right_count is None:
            return
        
        current_time = self.get_clock().now()
        dt = (current_time - self.last_time).nanoseconds / 1e9
        
        if dt == 0:
            return
        
        # Calculate distance traveled by each wheel
        left_delta = (left_count - self.left_encoder_last) / self.encoder_cpr * (2 * math.pi * self.wheel_radius)
        right_delta = (right_count - self.right_encoder_last) / self.encoder_cpr * (2 * math.pi * self.wheel_radius)
        
        # Update encoder positions
        self.left_encoder_last = left_count
        self.right_encoder_last = right_count
        
        # Calculate distance and angle change
        distance = (left_delta + right_delta) / 2.0
        delta_theta = (right_delta - left_delta) / self.wheel_separation
        
        # Update odometry
        self.x += distance * math.cos(self.theta + delta_theta / 2.0)
        self.y += distance * math.sin(self.theta + delta_theta / 2.0)
        self.theta += delta_theta
        
        # Normalize theta
        self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))
        
        # Publish Odometry message
        odom = Odometry()
        odom.header.stamp = current_time
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'
        
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0
        
        q = tf_transformations.quaternion_from_euler(0, 0, self.theta)
        odom.pose.pose.orientation.x = q[0]
        odom.pose.pose.orientation.y = q[1]
        odom.pose.pose.orientation.z = q[2]
        odom.pose.pose.orientation.w = q[3]
        
        # Velocities
        odom.twist.twist.linear.x = distance / dt if dt > 0 else 0.0
        odom.twist.twist.angular.z = delta_theta / dt if dt > 0 else 0.0
        
        self.odom_pub.publish(odom)
        
        # Publish TF transform
        t = TransformStamped()
        t.header.stamp = current_time
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]
        
        self.tf_broadcaster.sendTransform(t)
        
        self.last_time = current_time


def main(args=None):
    rclpy.init(args=args)
    node = SerialBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node.ser and node.ser.is_open:
            node.ser.close()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
