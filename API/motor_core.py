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
    

    """
    ----------------- TEMPORARY FUNCTIONS -----------------
    """

    """
    Stern starboard thruster, aft port thruster are CCW
    Stern port thruster, aft starboard thruster are CW

    When PWMs are greater than 1500 for Blue Robotics thrusters, the thrusters spin clockwise.
    Thrusters with a clockwise prop have a forward thrust vector when spinning clockwise.
    Thrusters with a counter clockwise prop have a backward thrust vector when spinning clockwise.
    """
    
    def surge(self, magnitude):
        """Configures for forward (positive magnitude) or backward (negative magnitude) movement"""
        self.t200.set_thrusters(magnitude, -magnitude, -magnitude, magnitude)

    def sway(self, magnitude):
        """Configures for right (positive magnitude) or left (negative magnitude) movement"""
        self.t200.set_thrusters(magnitude, magnitude, magnitude, magnitude)

    def yaw(self, magnitude):
        """Configures for clockwise (positive magnitude) or counterclockwise (negative magnitude)"""
        self.t200.set_thrusters(magnitude, magnitude, -magnitude, -magnitude)
    
    """
    --------------------------------------------------------
    """



    