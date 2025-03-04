from GNC.Nav_Core.info_core import infoCore
from GNC.Guidance_Core.mission_helper import MissionHelper
from GNC.Control_Core import motor_core_new
from GNC.Nav_Core import gis_funcs 
import cv2
import numpy as np
import time

def detect_buoy(frame, lower_bound, upper_bound):
    """Detects a buoy based on color range and returns its centroid."""
    mask = cv2.inRange(frame, lower_bound, upper_bound)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return (cx, cy)
    
    return None

def detect_buoy_red(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255])) + \
           cv2.inRange(hsv, np.array([170, 120, 70]), np.array([180, 255, 255]))
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) > 0:
            lowest_point = max(largest_contour, key=lambda point: point[0][1])  # Find point with max y-coordinate
            return tuple(lowest_point[0])  # (x, y)

    return (0, 0)

def detect_buoy_green(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Define HSV range for green color
    mask = cv2.inRange(hsv, np.array([40, 40, 40]), np.array([80, 255, 255]))
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) > 0:
            lowest_point = max(largest_contour, key=lambda point: point[0][1])  # Find point with max y-coordinate
            return tuple(lowest_point[0])  # (x, y)

    return (0, 0)


def navigate_boat(frame):
    """Processes the frame to detect buoys and determine navigation instructions."""
    # Convert frame to HSV
    
    # Define color ranges for red and green buoys
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])
    
    # Detect red and green buoys
    red_buoy = detect_buoy_red(frame)
    green_buoy = detect_buoy_green(frame)
    
    print(red_buoy)
    print(green_buoy)

    h, w, _ = frame.shape
    center_x = w // 2
    
    if red_buoy and green_buoy:
        gate_center_x = (red_buoy[0] + green_buoy[0]) // 2
        
        if gate_center_x < center_x - 20:
            command = "Turn Left"
        elif gate_center_x > center_x + 20:
            command = "Turn Right"
        else:
            command = "Move Forward"
    else:
        command = "Searching for buoys"
    
    return command, frame

"""***"""
config     = MissionHelper()
print("loading configs")
config     = config.load_json(path="GNC/Guidance_Core/Config/barco_polo.json")
info       = infoCore(modelPath=config["sign_model_path"],labelMap=config["sign_label_map"])
print("start background threads")
info.start_collecting()
motor      = motor_core_new.MotorCore("/dev/ttyACM2",debug=True) # load with default port "/dev/ttyACM2"
time.sleep(2)
print("rest 2 seconds")
GPS, _ = info.getInfo()
calc_lat, calc_lon = gis_funcs.destination_point(GPS.lat, GPS.lon, GPS.heading, 15)

try:

    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        gps, detections = info.getInfo()
        # cv2.imshow("Frame", info.getFrame())
        
        command, processed_frame = navigate_boat(info.getFrame())
        if command=="Turn Left":
            print("turn left")
            motor.veer(0.8,-0.4)
        elif command == "Turn Right":
            print("turn right")
            motor.veer(0.8,0.4)
        elif command == "Move Forward":
            print("surge")
            motor.surge(0.8)

        # TODO add stop statement
        if (gis_funcs.haversine(gps.lat,gps.lon,calc_lat,calc_lon)<=3): # 3 meter tolernace
            print("mission finished")
            info.stop_collecting()
            motor.stay()
            motor.stop()
            break

except KeyboardInterrupt:
    print("mission finished")
    info.stop_collecting()
    motor.stay()
    motor.stop()

info.stop_collecting()
motor.stay()
motor.stop()
    


