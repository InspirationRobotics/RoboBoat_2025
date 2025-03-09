from GNC.Control_Core.motor_core import MotorCore
import time

# Make motors
motors = MotorCore()

# Set speed to 1 for 40 seconds. Take out a stopwatch and learn
# how much time three rotations take, then change this argument
motors.rotate(1)
time.sleep(40)

motors.stay()
