import cv2
import numpy as np
import math
from API.Servos.mini_maestro import MiniMaestro
import time
import datetime

# === Calibration Constants ===
REAL_WIDTH_INCHES = 18.5
FOCAL_LENGTH = 588.3843844

#
maestro = MiniMaestro(port="/dev/ttyACM0")
launch_ball = False
start = datetime.datetime.now()
time_delay = 5 # seconds between each shot [seconds]

# Load video
#cap = cv2.VideoCapture('2025-02-16-151324.webm')
cap = cv2.VideoCapture(0)

save_frame = False

# Check if camera opened successfully
if not cap.isOpened():
    print("Error opening video file")
    exit()

# Get frame dimensions
ret, frame = cap.read()
if not ret:
    print("Failed to read first frame.")
    cap.release()
    exit()

height, width, _ = frame.shape

# Setup video writer
if save_frame:
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output2.avi', fourcc, 20.0, (width, height))

# Reset the capture position to frame 0
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

# Process video
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    image = frame.copy()
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # HSV Ranges
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 80, 100])
    lower_white = np.array([0, 0, 170])
    upper_white = np.array([180, 60, 255])

    # Masks
    mask_black = cv2.inRange(hsv, lower_black, upper_black)
    mask_white = cv2.inRange(hsv, lower_white, upper_white)

    # Morphology
    kernel = np.ones((5, 5), np.uint8)
    mask_black = cv2.morphologyEx(mask_black, cv2.MORPH_CLOSE, kernel)
    mask_black = cv2.morphologyEx(mask_black, cv2.MORPH_OPEN, kernel)
    mask_white = cv2.morphologyEx(mask_white, cv2.MORPH_CLOSE, kernel)
    mask_white = cv2.morphologyEx(mask_white, cv2.MORPH_OPEN, kernel)

    black_info = []
    black_centroids = []
    white_centroids = []

    # Find black contours
    contours_black, _ = cv2.findContours(mask_black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours_black:
        area = cv2.contourArea(cnt)
        if area > 1000:
            approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
            if len(approx) == 12:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.drawContours(image, [cnt], -1, (0, 255, 0), 3)
                cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(image, 'Black Cross', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                M = cv2.moments(cnt)
                if M['m00'] != 0.0:
                    c_x = int(M['m10'] / M['m00'])
                    c_y = int(M['m01'] / M['m00'])
                    black_centroids.append((c_x, c_y))
                    black_info.append(((c_x, c_y), w, h))
                    cv2.circle(image, (c_x, c_y), 10, (50, 168, 82), -1)

    # Find white contours
    contours_white, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours_white:
        area = cv2.contourArea(cnt)
        if area > 1000:
            approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
            if len(approx) >= 4:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.drawContours(image, [cnt], -1, (0, 255, 255), 3)
                cv2.rectangle(image, (x, y), (x+w, y+h), (255, 87, 51), 2)
                cv2.putText(image, 'White Square', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

                M = cv2.moments(cnt)
                if M['m00'] != 0.0:
                    c_x = int(M['m10'] / M['m00'])
                    c_y = int(M['m01'] / M['m00'])
                    white_centroids.append((c_x, c_y))
                    cv2.circle(image, (c_x, c_y), 10, (191, 64, 191), -1)

    # Find closest black centroid to white square
    min_distance = float('inf')
    closest_black = None
    closest_w = None
    closest_h = None

    for (bc, bw, bh) in black_info:
        for wc in white_centroids:
            dist = math.hypot(bc[0] - wc[0], bc[1] - wc[1])
            if dist < min_distance:
                min_distance = dist
                closest_black = bc
                closest_w = bw
                closest_h = bh

    # Highlight closest match and estimate distance
    if closest_black:
        estimated_distance = (REAL_WIDTH_INCHES * FOCAL_LENGTH) / closest_w
        print(f"Closest black cross centroid: {closest_black} | "
              f"Size: {closest_w}x{closest_h}px | "
              f"Distance: {estimated_distance:.2f} inches")

        cv2.circle(image, closest_black, 15, (0, 0, 255), 3)
        label = f'{closest_w}x{closest_h}px, {estimated_distance:.1f}"'
        cv2.putText(image, label, (closest_black[0] + 10, closest_black[1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        if estimated_distance <= 40:
            print(f"Distance: {estimated_distance:.2f} inches")
            launch_ball = True
        else: 
            launch_ball = False

    if launch_ball == True:
        sample_now = datetime.datetime.now()
        if sample_now.second > start.second + time_delay:
            start = datetime.datetime.now() # restarting the timer of when the last shot was
            maestro.set_pwm(0, 1800)  # Move servo on channel 0
            time.sleep(2)
            maestro.set_pwm(0, 1500)  # Move servo on channel 0



    # Show and save frame
    cv2.imshow("Detected Shapes", image)
    if save_frame:
        out.write(image)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# Clean up
cap.release()
if save_frame:
    out.release()
cv2.destroyAllWindows()
