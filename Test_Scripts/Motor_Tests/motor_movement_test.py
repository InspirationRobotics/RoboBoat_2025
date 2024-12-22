"""To test motor movements (surge sway yaw). Here's the plan:"""
import time
from API import motor_core

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

