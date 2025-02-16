#!/usr/bin/env python3
"""
Simple Autonomous Navigation Script:
- Uses GPS data to continuously update the boat’s position.
- Sets a starting waypoint (from the initial GPS fix) and a target waypoint (user input).
- Commands the boat to move forward at constant power until it reaches the target waypoint, then stops.
"""

import time
import math
import threading

from API.GPS.gps_api import GPS, GPSData
from GNC.Control_Core import motor_core

# ------------------------------
# Global Variable for GPS Data
# ------------------------------
current_gps = None
gps_lock = threading.Lock()

def gps_callback(data: GPSData):
    global current_gps
    with gps_lock:
        current_gps = data

def run_gps():
    gps = GPS('/dev/ttyUSB0', 115200, callback=gps_callback)
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        del gps

# ------------------------------
# Haversine Formula to Calculate Distance
# ------------------------------
def distance_between(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# ------------------------------
# Main Navigation Function
# ------------------------------
def main():
    # Instantiate MotorCore for controlling the boat's motors
    motors = motor_core.MotorCore("/dev/ttyACM0")
    
    # Wait for an initial GPS fix (this becomes our start waypoint)
    print("Waiting for initial GPS fix...")
    while True:
        with gps_lock:
            if current_gps is not None and current_gps.is_valid():
                start_lat = current_gps.lat
                start_lon = current_gps.lon
                break
        time.sleep(0.1)
    print(f"Initial GPS fix: lat={start_lat}, lon={start_lon}")
    
    # Define the starting waypoint as the current position
    start_waypoint = (start_lat, start_lon)
    
    # Get target waypoint from the user
    print("Enter target waypoint:")
    target_lat = float(input("  Latitude: "))
    target_lon = float(input("  Longitude: "))
    target_waypoint = (target_lat, target_lon)
    
    # Navigation loop: move forward until the target is reached
    threshold = 1.0  # meters
    print(f"Navigating from {start_waypoint} to {target_waypoint}...")
    try:
        while True:
            with gps_lock:
                if current_gps is None or not current_gps.is_valid():
                    continue
                curr_lat = current_gps.lat
                curr_lon = current_gps.lon
            dist = distance_between(curr_lat, curr_lon, target_lat, target_lon)
            print(f"Current position: ({curr_lat:.6f}, {curr_lon:.6f}), Distance to target: {dist:.2f} m")
            if dist <= threshold:
                print("Target reached!")
                motors.stop()
                break
            else:
                # Command a constant forward movement
                motors.surge(0.5)
            time.sleep(0.5)
    except KeyboardInterrupt:
        motors.stop()
        print("Navigation interrupted. Motors stopped.")

# ------------------------------
# Entry Point
# ------------------------------
if __name__ == "__main__":
    # Start the GPS thread
    gps_thread = threading.Thread(target=run_gps, daemon=True)
    gps_thread.start()
    main()
