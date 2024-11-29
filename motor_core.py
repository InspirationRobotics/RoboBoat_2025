"""
To aggregate/integrate the various higher-level files (sensor fusion, perception, etc),
and create a single list of values to be sent to the Arduino to actuate the motors.
"""
# TODO: Everything.

import serial
import time

class MotorCore():
    def __init__(self, port = "/dev/tty/ACM0"):
        arduino = serial.Serial(port = port, baudrate = 9600)
        time.sleep(1)


    