"""
To aggregate/integrate the various higher-level files (sensor fusion, perception, etc),
and create a single list of values to be sent to the Arduino to actuate the motors.
"""

import serial
import time

from . import t200

class MotorCore():
    def __init__(self, port = "/dev/ttyACM0"):
        self.t200 = t200(port="/dev/ttyACM0")
    
    # TODO: Water test the basic movement functions (forward, lateral, yaw)
    def forward(self, magnitude):
        """Makes the boat move forward by the specified magnitude."""
        self.t200.set_thrusters(magnitude, magnitude, -magnitude, magnitude)


    