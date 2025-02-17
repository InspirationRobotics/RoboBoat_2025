"""
Simple test to determine whether the motor_core GPS code works.

The test is considered successful if nothing crashes and the motor_core threads join after 10 seconds.
"""

import time
from GNC.Control_Core import motor_core

motor_port = "/dev/ttyACM0"
motors = motor_core.MotorCore(motor_port)

motors.main()
time.sleep(2)
