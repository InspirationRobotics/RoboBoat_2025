import time
from GNC.Control_Core import motor_core
motors = motor_core.MotorCore("/dev/ttyACM0")

user_input = input("command>> ")
while(True):
        if(str(user_input) == ("r")):
                print("performing triangular orientation. BRACE YOURSELF!")
                start = time.perf_counter_ns()

                """0th stage, rotation intializer for 1st stage"""
                start_S1 = time.perf_counter_ns()
                motors.rotate(-1)
                time.sleep(1)

                """1st stage, surge forward, sleep for 1 sec"""
                motors.surge(5)
                end_S1 = time.perf_counter_ns()
                print(f"Stage 1 performed in {end_S1 - start_S1} nanoseconds")
                time.sleep(1)

                """2nd stage, rotate 60 degrees, sleep for 1 sec,
                surge forward, then sleep for 1 sec """
                start_S2 = time.perf_counter_ns()
                motors.rotate(-2)
                time.sleep(1)
                motors.surge(5)
                end_S2 = time.perf_counter_ns()
                print(f"Stage 2 performed in {end_S2 - start_S2} nanoseconds"
                time.sleep(1)

jgjgojgimport time
from GNC.Control_Core import motor_core

# Initialize motor core
motors = motor_core.MotorCore("/dev/ttyACM0")

while True:
    user_input = input("command>> ").strip().lower()  # Get user input and clean it
    if user_input == "r":
        print("Performing triangular orientation. BRACE YOURSELF!")
        start = time.perf_counter_ns()

        # 0th stage: Rotation initializer for 1st stage
        start_S1 = time.perf_counter_ns()
        motors.rotate(-1)
        time.sleep(1)

        # 1st stage: Surge forward
        motors.surge(5)
        end_S1 = time.perf_counter_ns()
        print(f"Stage 1 performed in {end_S1 - start_S1} nanoseconds")
        time.sleep(1)

        # 2nd stage: Rotate 60 degrees, surge forward
        start_S2 = time.perf_counter_ns()
        motors.rotate(-2)
        time.sleep(1)
        motors.surge(5)
        end_S2 = time.perf_counter_ns()
        print(f"Stage 2 performed in {end_S2 - start_S2} nanoseconds")
        time.sleep(1)

        # 3rd stage: Rotate 60 degrees, surge forward, finalize orientation
        start_S3 = time.perf_counter_ns()
        motors.rotate(-2)
        time.sleep(1)
        motors.surge(5)
        time.sleep(1)

        motors.rotate(3)  # Return to initial position
        end_S3 = time.perf_counter_ns()
        print(f"Stage 3 performed in {end_S3 - start_S3} nanoseconds")

        # Finalize and stop motors
        motors.stop()
        print(f"Orientation completed in {end_S3 - start} nanoseconds")

    elif user_input == "q":
        print("Exiting program. Stopping motors.")
        motors.stop()
        break  # Exit the infinite loop

    else:
        print("Invalid command. Use 'r' to run or 'q' to quit.")
                """3rd stage, rotate 60 degrees, sleep for 1 sec, surge forward, then sleep for 1 sec, then rotate 90 degrees to initial position"""
                start_S3 = time.perf_counter_ns()
                motors.rotate(-2)
                time.sleep(1)
                motors.surge(5)
                time.sleep(1)

                """finalize and stop orientation run"""
                end_S3 = time.perf_counter_ns()
                print(f"Performed in {end_S3 - start_S3} nanoseconds")

        if(str(user_input) == ("q")):
                print("quitting the code")
                start = time.perf_counter_ns()
                motors.stop()
                end = time.perf_counter_ns()
                print(f"time elapsed to quit: {end - start}")
                break
