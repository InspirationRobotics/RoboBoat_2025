# Import necessary libraries
import cv2
import numpy as np

# Path to the input video
video_path = '/Users/parsasedighi/Documents/GitHub/RoboBoat_2025/GNC/Guidance_Core/Missions/2025-04-13-145055.webm'

# Create a VideoCapture object
cap = cv2.VideoCapture(video_path)

# Threshold for contour area
CONTOUR_AREA_THRESHOLD = 100

def detect_buoy_green(frame):
    """Detect green buoys in the frame and return the lowest point and modified frame."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([40, 40, 40]), np.array([80, 255, 255]))

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    h, w, _ = frame.shape

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        
        if cv2.contourArea(largest_contour) > CONTOUR_AREA_THRESHOLD:
            # Find the point with the maximum Y (lowest point)
            lowest_point = max(largest_contour, key=lambda point: point[0][1])
            x, y = tuple(lowest_point[0])

            # Draw on the frame
            cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)  # Green contour
            cv2.circle(frame, (x, y), 5, (255, 0, 0), -1)  # Blue dot on the lowest point
            cv2.circle(frame, (0, 0), 5, (255, 0, 0), -1)  # Blue dot at top-left corner
            cv2.circle(frame, (w, h), 5, (255, 255, 0), -1)  # Yellow dot at bottom-right corner

            return (x, y), frame

    return None, frame

# Verify video is opened successfully
if not cap.isOpened():
    print("Error: Could not open video file.")
    exit()

# Process video frame-by-frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    _, processed_frame = detect_buoy_green(frame)
    cv2.imshow('Processed Frame', processed_frame)

    # Press 'q' to quit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()