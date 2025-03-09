from GNC.Control_Core import motor_core
import time

# Make motors
motors = motor_core.MotorCore("/dev/ttyACM2")

# Set speed to 1 for 40 seconds. Take out a stopwatch and learn
# how much time three rotations take, then change this argument
try:
    motors.rotate(0.5)
    time.sleep(20)
    motors.stay()
except KeyboardInterrupt:
    motors.stop()
    
