import time
from GNC.Control_Core import motor_core

motor_port = "/dev/ttyACM0"
motors = motor_core.MotorCore(motor_port)

# Initialize and wait for the motor system
print("Waiting...")
time.sleep(5)

# Main function for navigation using waypoints from CSV
motors.main(waypoint_file="/API/GPS/waypoint_data/20250220_miramar_testingcoordinates.csv", duration=20)

# If you want to navigate to specific coordinates after that:
# desired_lat = 34.0522  # example latitude
# desired_lon = -118.2437  # example longitude
# motors.lat_lon_navigation(desired_lat, desired_lon)

# Exit after navigation
motors.exit()
