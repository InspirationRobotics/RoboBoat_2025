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
from GNC.Control_Core import motor_core

motors = motor_core.MotorCore("/dev/ttyACM0")


while(True):
    user_input = input("command>> ")
    if(str(user_input) == "q"):
        print("quiting the code")
        start = time.perf_counter_ns()
        motors.stop()
        end = time.perf_counter_ns()
        print(f"Takes {end-start} ns to stop")
        break
    elif(str(user_input) == "w"):
        start = time.perf_counter_ns()
        motors.surge(0.5)
        end = time.perf_counter_ns()
        print(f"elapsed time: {end-start} ns")
    elif (str(user_input) == "s"):
        start = time.perf_counter_ns()
        motors.surge(-0.5)
        end = time.perf_counter_ns()
        print(f"elapsed time: {end - start} ns")
    elif(str(user_input) =="a"):
        start = time.perf_counter_ns()
        motors.slide(0.5)
        end = time.perf_counter_ns()
        print(f"elapsed time: {end-start} ns")
    elif(str(user_input) =="d"):
        start = time.perf_counter_ns()
        motors.slide(-0.5)
        end = time.perf_counter_ns()
        print(f"elapsed time: {end - start} ns")
    elif(str(user_input) =="0"):
        start = time.perf_counter_ns()
        motors.stay()
        end = time.perf_counter_ns()
        print(f"elapsed time: {end - start} ns")



