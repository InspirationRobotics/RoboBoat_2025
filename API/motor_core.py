"""
To aggregate/integrate the various higher-level files (sensor fusion, perception, etc),
and create a single list of values to be sent to the Arduino to actuate the motors.
"""

import serial
import time

from . import t200

class MotorCore():
    def __init__(self, port = "/dev/tty/ACM0"):
        self.t200 = t200(port="dev/tty/ACM0")


    