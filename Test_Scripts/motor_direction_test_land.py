"""This is a motor direction test. It will run each of the motors at a slow forward speed for 1.5 seconds each.
It is meant to distinguish which argument maps to which thruster and the directionalities of the thrusters for forward
power (forwards or backwards). This a land test!"""

import time
from API import t200

# Double-check to see if the hardcoded port /tty/ACM0 is correct
motors = t200.T200()

# Run each thruster slowly forward for 5 secs
motors.set_thrusters(0.16, 0, 0, 0)
time.sleep(5)
motors.set_thrusters(0, 0.16, 0, 0)
time.sleep(5)
motors.set_thrusters(0, 0, 0.16, 0)
time.sleep(5)
motors.set_thrusters(0, 0, 0, 0.16)
time.sleep(5)

motors.stop_thrusters()