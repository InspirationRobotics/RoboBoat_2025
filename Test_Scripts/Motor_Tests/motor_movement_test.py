"""
To test motor movements (surge sway yaw).

The test is considered successful if:
- The ASV moves forward for 7.5 seconds.
- The ASV moves backwards for 7.5 seconds.
- The ASV strafes (moves laterally) right for 7.5 seconds.
- The ASV strafes left for 7.5 seconds.
- The ASV yaws clockwise for 7.5 seconds.
- The ASV yaws counterclockwise for 7.5 seconds.
"""

import time
from GNC import motor_core

motors = motor_core.MotorCore("/dev/ttyACM0")

# Try moving forward for 7.5 seconds at 0.5 speed
motors.surge(0.5)
time.sleep(7.5)

# Try moving backward for 7.5 seconds at 0.5 speed
motors.surge(-0.5)
time.sleep(7.5)

# Try moving right for 7.5 seconds at 0.5 speed
motors.sway(0.5)
time.sleep(7.5)

# Try moving left for 7.5 seconds at 0.5 speed
motors.sway(-0.5)
time.sleep(7.5)

# Try yawing right for 7.5 seconds at 0.5 speed
motors.yaw(0.5)
time.sleep(7.5)

# Try yawing left for 7.5 seconds at 0.5 speed
motors.yaw(-0.5)
time.sleep(7.5)

