import cv2
import numpy as np
import math
from API.Servos.mini_maestro import MiniMaestro
import time

# === Calibration Constants ===
REAL_WIDTH_INCHES = 18.5
FOCAL_LENGTH = 588.3843844
TIME_DELAY = 5  # seconds between each shot
LAUNCH_DISTANCE_THRESHOLD = 40  # inches

# HSV color bounds
LOWER_BLACK = np.array([0, 0, 0])
UPPER_BLACK = np.array([180, 80, 100])
LOWER_WHITE = np.array([0, 0, 170])
UPPER_WHITE = np.array([180, 60, 255])

KERNEL = np.ones((5, 5), np.uint8)


def init_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise IOError("Cannot open camera")
    return cap


def get_frame_dimensions(cap):
    ret, frame = cap.read()
    if not ret:
        raise IOError("Cannot read frame from camera")
    return frame.shape[:2]  # height, width


def process_frame(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask_black = cv2.inRange(hsv, LOWER_BLACK, UPPER_BLACK)
    mask_white = cv2.inRange(hsv, LOWER_WHITE, UPPER_WHITE)

    # Morphology
    mask_black = cv2.morphologyEx(mask_black, cv2.MORPH_CLOSE, KERNEL)
    mask_black = cv2.morphologyEx(mask_black, cv2.MORPH_OPEN, KERNEL)
    mask_white = cv2.morphologyEx(mask_white, cv2.MORPH_CLOSE, KERNEL)
    mask_white = cv2.morphologyEx(mask_white, cv2.MORPH_OPEN, KERNEL)

    return mask_black, mask_white


def find_contours(mask, shape_name='black'):
    centroids = []
    info = []
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 1000:
            approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)

            if shape_name == 'black' and len(approx) == 12:
                M = cv2.moments(cnt)
                if M['m00'] != 0:
                    c_x = int(M['m10'] / M['m00'])
                    c_y = int(M['m01'] / M['m00'])
                    x, y, w, h = cv2.boundingRect(cnt)
                    centroids.append((c_x, c_y))
                    info.append(((c_x, c_y), w, h))

            elif shape_name == 'white' and len(approx) >= 4:
                M = cv2.moments(cnt)
                if M['m00'] != 0:
                    c_x = int(M['m10'] / M['m00'])
                    c_y = int(M['m01'] / M['m00'])
                    centroids.append((c_x, c_y))

    return centroids, info if shape_name == 'black' else centroids


def find_closest_match(black_info, white_centroids):
    min_distance = float('inf')
    closest = None

    for (bc, bw, bh) in black_info:
        for wc in white_centroids:
            dist = math.hypot(bc[0] - wc[0], bc[1] - wc[1])
            if dist < min_distance:
                min_distance = dist
                closest = (bc, bw, bh)
    return closest


def estimate_distance(pixel_width):
    return (REAL_WIDTH_INCHES * FOCAL_LENGTH) / pixel_width


def launch(maestro):
    maestro.set_pwm(0, 1800)
    time.sleep(2)
    maestro.set_pwm(0, 1500)


def main():
    maestro = MiniMaestro(port="/dev/ttyACM0")
    cap = init_camera()
    last_shot_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        mask_black, mask_white = process_frame(frame)
        black_centroids, black_info = find_contours(mask_black, 'black')
        white_centroids = find_contours(mask_white, 'white')

        match = find_closest_match(black_info, white_centroids)
        if match:
            closest_black, closest_w, closest_h = match
            distance = estimate_distance(closest_w)

            print(f"Target at {distance:.2f} inches.")

            if distance <= LAUNCH_DISTANCE_THRESHOLD and time.time() - last_shot_time >= TIME_DELAY:
                launch(maestro)
                print("Ball launched!")
                last_shot_time = time.time()

        # Display result
        cv2.imshow("Vision", frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
