"""
To aggregate/integrate the various higher-level files (sensor fusion, perception, etc),
and create a single list of values to be sent to the Arduino to actuate the motors.
"""

import serial
import time

# NOTE: Not sure whether absolute imports will work
from API.Motors import t200

class MotorCore():
    def __init__(self, port = "/dev/ttyACM0"):
        self.t200 = t200(port="/dev/ttyACM0")
    
    def surge(self, magnitude):
        """Configures for forward (positive magnitude) or backward (negative magnitude) movement"""
        self.t200.set_thrusters(magnitude, -magnitude, -magnitude, magnitude)

    def sway(self, magnitude):
        """Configures for right (positive magnitude) or left (negative magnitude) movement"""
        self.t200.set_thrusters(magnitude, magnitude, magnitude, magnitude)

    def yaw(self, magnitude):
        """Configures for clockwise (positive magnitude) or counterclockwise (negative magnitude)"""
        self.t200.set_thrusters(magnitude, magnitude, -magnitude, -magnitude)
    



    