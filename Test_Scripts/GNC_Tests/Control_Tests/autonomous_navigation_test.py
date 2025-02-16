#!/usr/bin/env python3
"""
Autonomous Navigation with Multiple Waypoints:
This script uses GPS data and PID controllers to autonomously drive the boat
through a series of waypoints. You can enter two waypoints, and the boat will
attempt to navigate to them sequentially.
"""

import time
import math
import threading

from API.GPS.gps_api import GPS, GPSData
from GNC.Control_Core import motor_core

# ==============================
# PID Controller Class
# ==============================
class PIDController:
    def __init__(self, kp, ki, kd, output_limits=(-0.5, 0.5)):
        self.kp = 1
        self.ki = 0.1
        self.kd = 0.05
        self.integral = 0.0
        self.prev_error = 0.0
        self.last_time = None
        self.output_limits = output_limits

    def update(self, error, current_time):
        if self.last_time is None:
            dt = 0.1  # initial assumption
        else:
            dt = current_time - self.last_time
        self.last_time = current_time

        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
        self.prev_error = error

        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        min_out, max_out = self.output_limits
        output = max(min_out, min(output, max_out))
        return output

# ==============================
# Global Variable for GPS Data
# ==============================
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

# ==============================
# Coordinate Conversion Function
# ==============================
def latlon_to_xy(lat, lon, ref_lat, ref_lon):
    R = 6371000  # Earth radius in meters
    dlat = math.radians(lat - ref_lat)
    dlon = math.radians(lon - ref_lon)
    avg_lat = math.radians((lat + ref_lat) / 2.0)
    x = dlon * math.cos(avg_lat) * R  # east-west displacement (meters)
    y = dlat * R                     # north-south displacement (meters)
    return x, y

# ==============================
# Navigation Function for a Single Waypoint
# ==============================
def navigate_to_waypoint(motors, target_lat, target_lon, ref_lat, ref_lon):
    surge_pid = PIDController(kp=0.001, ki=0.0001, kd=0.0005, output_limits=(-0.5, 0.5))
    slide_pid = PIDController(kp=0.001, ki=0.0001, kd=0.0005, output_limits=(-0.5, 0.5))
    
    print(f"Navigating to waypoint: lat={target_lat}, lon={target_lon}")
    while True:
        current_time = time.time()
        with gps_lock:
            if current_gps is None:
                continue
            current_lat = current_gps.lat
            current_lon = current_gps.lon
            boat_heading = math.radians(current_gps.heading)

        current_x, current_y = latlon_to_xy(current_lat, current_lon, ref_lat, ref_lon)
        target_x, target_y = latlon_to_xy(target_lat, target_lon, ref_lat, ref_lon)

        error_x = target_x - current_x  # east error
        error_y = target_y - current_y  # north error

        distance_error = math.hypot(error_x, error_y)
        if distance_error < 1.0:  # waypoint reached if within 1 meter
            print("Waypoint reached!")
            motors.stop()
            time.sleep(2)  # brief pause before moving to the next waypoint
            break

        # Transform error to boat frame
        surge_error = error_y * math.cos(boat_heading) + error_x * math.sin(boat_heading)
        slide_error = error_x * math.cos(boat_heading) - error_y * math.sin(boat_heading)

        surge_command = surge_pid.update(surge_error, current_time)
        slide_command = slide_pid.update(slide_error, current_time)

        motors.surge(surge_command)
        motors.slide(slide_command)

        print(f"Distance: {distance_error:.2f} m | Surge Error: {surge_error:.2f} | Slide Error: {slide_error:.2f}")
        print(f"Commands -> Surge: {surge_command:.2f}, Slide: {slide_command:.2f}")
        time.sleep(0.1)

# ==============================
# Main Autonomous Navigation Loop
# ==============================
def main():
    motors = motor_core.MotorCore("/dev/ttyACM0")

    # Define waypoints: You can either prompt the user or hardcode them
    print("Enter waypoint 1:")
    wp1_lat = float(input("  Latitude: "))
    wp1_lon = float(input("  Longitude: "))

    print("Enter waypoint 2:")
    wp2_lat = float(input("  Latitude: "))
    wp2_lon = float(input("  Longitude: "))

    waypoints = [(wp1_lat, wp1_lon), (wp2_lat, wp2_lon)]

    # Wait for initial GPS fix to set the reference coordinate
    print("Waiting for initial GPS fix...")
    while True:
        with gps_lock:
            if current_gps is not None:
                current_lat = current_gps.lat
                current_lon = current_gps.lon
                break
        time.sleep(0.1)
    print(f"Initial GPS fix: lat={current_lat}, lon={current_lon}")
    ref_lat, ref_lon = current_lat, current_lon

    # Navigate through each waypoint sequentially
    for i, (target_lat, target_lon) in enumerate(waypoints, start=1):
        print(f"Starting navigation to Waypoint {i}")
        navigate_to_waypoint(motors, target_lat, target_lon, ref_lat, ref_lon)

    print("All waypoints reached. Stopping the boat.")
    motors.stop()

# ==============================
# Entry Point
# ==============================
if __name__ == "__main__":
    gps_thread = threading.Thread(target=run_gps, daemon=True)
    gps_thread.start()
    main()
