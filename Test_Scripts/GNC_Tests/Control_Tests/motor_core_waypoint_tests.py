"""
Test to determine whether lat, lon GPS navigation works. Also tests the exit() function.
NOTE: YOU MUST SET THE (lat, lon) COORDINATES BEFORE RUNNING THIS FILE.

This test is considered successful if the ASV is able to navigate to the desired lat, lon coordinates.
"""

import time
from GNC.Control_Core import motor_core

motor_port = "/dev/ttyACM0"
motors = motor_core.MotorCore(motor_port)

motors.main(duration=20)
print("Waiting...")
time.sleep(5)

# TODO: Change these.
desired_lat = 32.923590
desired_lon = -117.038501

motors.lat_lon_navigation(desired_lat, desired_lon)
time.sleep(15)
motors.exit()

