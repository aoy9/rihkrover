#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory  # Changed for Pi 4
import time

# Helper function to map ranges
def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

class MotorBridge(Node):
    def __init__(self):
        super().__init__('motor_bridge')

        # --- Pi 4 Hardware PWM Setup ---
        # This tells gpiozero to use the pigpio daemon for jitter-free timing
        factory = PiGPIOFactory()
        
        self.motor1 = Servo(18, min_pulse_width=0.0011, max_pulse_width=0.0019, pin_factory=factory)
        self.motor2 = Servo(23, min_pulse_width=0.0011, max_pulse_width=0.0019, pin_factory=factory)

        self.get_logger().info("Arming Motors (Wait 3 sec)...")
        self.motor1.value = 0
        self.motor2.value = 0
        time.sleep(3)

        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10)
        
        self.max_linear_vel = 0.5  # m/s
        self.max_angular_vel = 1.0 # rad/s

        self.get_logger().info("Pi 4 Motor Bridge Ready! Listening to /cmd_vel...")

    def cmd_vel_callback(self, msg):
        v = msg.linear.x 
        w = msg.angular.z 

        # 1. Standard Differential Math
        norm_v = max(min(v / self.max_linear_vel, 1.0), -1.0)
        norm_w = max(min(w / self.max_angular_vel, 1.0), -1.0)

        raw_left = norm_v - norm_w
        raw_right = norm_v + norm_w

        raw_left = max(min(raw_left, 1.0), -1.0)
        raw_right = max(min(raw_right, 1.0), -1.0)

        # 2. YOUR CALIBRATED MAPPING
        # MOTOR 1 (Left) Calibration:
        if raw_left > 0:
            m1_val = map_range(raw_left, 0.0, 1.0, 0.0, -0.025)
        elif raw_left < 0:
            m1_val = map_range(raw_left, 0.0, -1.0, 0.0, 0.4)
        else:
            m1_val = 0.0

        # MOTOR 2 (Right) Calibration:
        if raw_right > 0:
            m2_val = map_range(raw_right, 0.0, 1.0, 0.0, 0.4)
        elif raw_right < 0:
            m2_val = map_range(raw_right, 0.0, -1.0, 0.0, -0.025)
        else:
            m2_val = 0.0

        # 3. Send to hardware
        self.motor1.value = m1_val
        self.motor2.value = m2_val

def main(args=None):
    rclpy.init(args=args)
    node = MotorBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.motor1.value = 0
        node.motor2.value = 0
        node.motor1.close()
        node.motor2.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
