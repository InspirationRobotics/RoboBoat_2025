import cv2
import numpy as np

def detect_buoy_green(frame):
    """
    Detect green buoys in the frame and return the mask and the modified frame.
    """
    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define HSV range for green
    lower_green = np.array([30, 100, 190])
    upper_green = np.array([85, 255, 255])

    # Create a binary mask where green colors are white
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    h, w, _ = frame.shape

    if contours:
        # Find the largest contour
        largest_contour = max(contours, key=cv2.contourArea)

        # Only consider contours with sufficient area
        if cv2.contourArea(largest_contour) > 100:
            # Find the lowest point on the contour (max Y coordinate)
            lowest_point = max(largest_contour, key=lambda point: point[0][1])
            x, y = tuple(lowest_point[0])

            # Draw the contour and the lowest point
            cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)  # Green contour
            cv2.circle(frame, (x, y), 5, (255, 0, 0), -1)  # Blue dot at lowest point

    return mask, frame

# === VIDEO SETUP ===
video_path = '/Users/parsasedighi/Documents/GitHub/RoboBoat_2025/GNC/Guidance_Core/Missions/2025-04-13-145055.webm'
cap = cv2.VideoCapture(video_path)

# Check if video opened successfully
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# === MAIN LOOP ===
while True:
    ret, frame = cap.read()
    if not ret:
        print("End of video or failed to read frame.")
        break

    # Detect green buoy and get processed frame + mask
    mask, processed_frame = detect_buoy_green(frame)

    # Display the results
    cv2.imshow('Original Frame', frame)
    cv2.imshow('Mask', mask)
    cv2.imshow('Processed Frame', processed_frame)

    # Press 'q' to quit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# === CLEANUP ===
cap.release()
cv2.destroyAllWindows()