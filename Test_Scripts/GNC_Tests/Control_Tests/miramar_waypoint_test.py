import queue
import time
import threading
import csv  # Fix: Import csv module
from typing import List, Tuple
from GNC.Control_Core import motor_core
from GNC.Nav_Core import gis_funcs

# Initialize motors
motor_port = "/dev/ttyACM2"
motors = motor_core.MotorCore(motor_port)

# Wait for the motor system to initialize
print("Waiting...")
time.sleep(5)

# Number of times to iterate through waypoints
iterations = 3

def load_waypoints(file_path: str) -> List[Tuple[float, float]]:
    """
    Load waypoints (latitude, longitude, heading) from a CSV file.
    Args:
        file_path (str): Path to the data file.
    Returns:
        List[Tuple[float, float, float]]: List of waypoints (latitude, longitude, heading).
    """
    waypoints = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            lat = float(row['latitude'])
            lon = float(row['longitude'])
            waypoints.append((lat, lon))
    return waypoints

def has_reached_target(motors, tolerance=2.0) -> bool:
    """
    Check if the vehicle has reached the target position within a given tolerance.
    """
    current_position = motors.position_data.get("current_position")
    if current_position is None:
        motors.stop()
        motors.exit()
        return False
    
    distance_to_target = gis_funcs.haversine(
        current_position[0], current_position[1],
        motors.desired_position[0], motors.desired_position[1]
    )
    return abs(distance_to_target) <= tolerance  

def main(waypoint_file: str, calculate_rate=0.1, send_rate=0.1):
    """
    Main function to execute waypoints a fixed number of times.
    """
    waypoints = load_waypoints(waypoint_file)

    # Start motor control threads once
    send_queue = queue.Queue()
    motors.stop_event = threading.Event()
    
    motors.control_loop_instance = threading.Thread(target=motors.control_loop, args=(send_queue, send_rate, motors.stop_event))
    motors.control_loop_instance.daemon = True
    motors.control_loop_instance.start()

    motors.calc_motor_power_instance = threading.Thread(target=motors.calc_motor_power, args=(send_queue, calculate_rate, motors.stop_event))
    motors.calc_motor_power_instance.daemon = True
    motors.calc_motor_power_instance.start()

    # Execute waypoints for a fixed number of iterations
    for _ in range(iterations):
        for lat, lon in waypoints:
            motors.desired_position = (lat, lon)
            motors.lat_lon_navigation(lat, lon)

            print(f"Navigating to waypoint: {lat}, {lon}")

            # Wait until the target is reached
            while not has_reached_target(motors):
                time.sleep(0.5) 
        
            print(f"Reached waypoint: {lat}, {lon}")

    # Clean up threads
    motors.stop_event.set()
    motors.calc_motor_power_instance.join()
    motors.control_loop_instance.join()
    motors.stop()

    print("[MOTOR CORE] Navigation completed.")

# Run navigation
load_waypoints(file_path="miramar.csv")
main(waypoint_file="miramar.csv")

# Exit after navigation
motors.exit()
