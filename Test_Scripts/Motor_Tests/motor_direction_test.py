"""This is a motor direction test. It will run each of the motors at a moderate forward speed for 4 seconds each.
It is meant to distinguish which argument maps to which thruster and the directionalities of the thrusters for forward
power (forwards or backwards). This an in-water test!"""

import time
from API.Motors import t200

# Double-check to see if the hardcoded port /tty/ACM0 is correct
motors = t200.T200()

# Run each thruster moderately forward for 4 secs
motors.set_thrusters(0.5, 0, 0, 0)
time.sleep(4)
motors.set_thrusters(0, 0.5, 0, 0)
time.sleep(4)
motors.set_thrusters(0, 0, 0.5, 0)
time.sleep(4)
motors.set_thrusters(0, 0, 0, 0.5)
time.sleep(4)

motors.stop_thrusters()