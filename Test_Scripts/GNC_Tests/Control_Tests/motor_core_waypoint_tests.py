"""
Test to determine whether lat, lon GPS navigation works. Also tests the exit() function.
NOTE: YOU MUST SET THE (lat, lon) COORDINATES BEFORE RUNNING THIS FILE.

This test is considered successful if the ASV is able to navigate to the desired lat, lon coordinates.
"""

import time
from GNC.Control_Core import motor_core

motor_port = "/dev/ttyACM2"
motors = motor_core.MotorCore(motor_port)
print("Waiting...")
time.sleep(5)

motors.main(duration=20)

# TODO: Change these.
desired_lat = 32.914415207734535
desired_lon = -117.10090419685663

motors.lat_lon_navigation(desired_lat, desired_lon)
motors.exit()

