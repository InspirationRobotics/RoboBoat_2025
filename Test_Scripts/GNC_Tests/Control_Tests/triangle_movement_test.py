"""20250214 test script for motor movement test in a triangle orientation.
A successful test should show the following:
        - surge for 3 seconds
        -
        -
"""
import time
from GNC.Control_Core import motor_core

motors = motor_core.MotorCore("/dev/ttyACM0")

while(True):
        if(str(user_input) == ("r"):
                print("performing triangular orientation. BRACE YOURSELF!")
                start = time.perf_counter_ns()

                """0th stage, rotation intializer for 1st stage"""
                start_S1 = time.perf_counter_ns()
                rotate(-1)
                time.sleep(1)

                """1st stage, surge forward, sleep for 1 sec"""
                surge(5)
                end_S1 = time.perf_counter_ns()
                print(f"Stage 1 performed in {end - start} nanoseconds")
                time.sleep(1)

                """2nd stage, rotate 60 degrees, sleep for 1 sec,
                surge forward, then sleep for 1 sec """
                rotate(-2)
                time.sleep(1)
                surge(5)
                time.sleep(1)


                """3rd stage, rotate 60 degrees, sleep for 1 sec, surge forward, then sleep for 1 sec, then rotate 90 degrees to initial position"""
                rotate(
                rotate(-2)
                time.sleep(1)
                surge(5)
                time.sleep(1)

                """finalize and stop orientation run"""
                end = time.perf_counter_ns()
                print(f"Performed in {end - start} nanoseconds")

        if(str(user_input) == ("q")):
                print("quitting the code")
                start = time.perf_counter_ns()
                motors.stop()
                end = time.perf_counter_ns()
                print(f"time elapsed to quit: {end - start}")
                break

