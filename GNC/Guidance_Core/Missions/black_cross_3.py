import cv2
import numpy as np
import math
from API.Servos.mini_maestro import MiniMaestro
from API.Servos.ardiuno_compound import ArdiunoCompound

import time

# === Calibration Constants ===
REAL_WIDTH_INCHES = 18.5
FOCAL_LENGTH = 588.3843844
TIME_DELAY = 5
LAUNCH_DISTANCE_THRESHOLD = 40

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


def process_frame(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask_black = cv2.inRange(hsv, LOWER_BLACK, UPPER_BLACK)
    mask_white = cv2.inRange(hsv, LOWER_WHITE, UPPER_WHITE)

    mask_black = cv2.morphologyEx(mask_black, cv2.MORPH_CLOSE, KERNEL)
    mask_black = cv2.morphologyEx(mask_black, cv2.MORPH_OPEN, KERNEL)
    mask_white = cv2.morphologyEx(mask_white, cv2.MORPH_CLOSE, KERNEL)
    mask_white = cv2.morphologyEx(mask_white, cv2.MORPH_OPEN, KERNEL)

    return mask_black, mask_white


def find_contours(mask, frame, shape_name='black'):
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

                    # Draw visuals
                    cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.putText(frame, 'Black Cross', (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.circle(frame, (c_x, c_y), 8, (0, 128, 0), -1)

                    centroids.append((c_x, c_y))
                    info.append(((c_x, c_y), w, h))

            elif shape_name == 'white' and len(approx) >= 4:
                M = cv2.moments(cnt)
                if M['m00'] != 0:
                    c_x = int(M['m10'] / M['m00'])
                    c_y = int(M['m01'] / M['m00'])
                    x, y, w, h = cv2.boundingRect(cnt)

                    # Draw visuals
                    cv2.drawContours(frame, [cnt], -1, (0, 255, 255), 2)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 87, 51), 2)
                    cv2.putText(frame, 'White Square', (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                    cv2.circle(frame, (c_x, c_y), 8, (191, 64, 191), -1)

                    centroids.append((c_x, c_y))

    return (centroids, info) if shape_name == 'black' else (centroids, [])


def find_closest_match(black_info, white_centroids):
    min_distance = float('inf')
    closest = None

    for (bc, bw, bh) in black_info:
        for wc in white_centroids:
            if not isinstance(wc, tuple) or len(wc) != 2:
                continue
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

def launch_ardiuno(ardiuno_compound):
    # Send simple character command
    ardiuno_compound.send_command("g")  # Will now send as bytes: b'g'
    time.sleep(2)
    ardiuno_compound.send_command("a")  # reloading

def main():
        # Change port based on your system (e.g., "COM3" on Windows, "/dev/ttyUSB0" on Linux/Mac)
    ardiuno_compound = ArdiunoCompound(port="/dev/ttyACM3")

    maestro = MiniMaestro(port="/dev/ttyACM0")
    cap = init_camera()
    last_shot_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        mask_black, mask_white = process_frame(frame)
        black_centroids, black_info = find_contours(mask_black, frame, 'black')
        white_centroids, _ = find_contours(mask_white, frame, 'white')

        match = find_closest_match(black_info, white_centroids)
        if match:
            closest_black, closest_w, closest_h = match
            distance = estimate_distance(closest_w)

            cv2.circle(frame, closest_black, 15, (0, 0, 255), 3)
            cv2.putText(frame, f'{closest_w}x{closest_h}px, {distance:.1f}"',
                        (closest_black[0] + 10, closest_black[1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            print(f"Target at {distance:.2f} inches")

            if distance <= LAUNCH_DISTANCE_THRESHOLD and time.time() - last_shot_time >= TIME_DELAY:
                #launch(maestro)
                launch_ardiuno(ardiuno_compound)

                print("Ball launched!")
                last_shot_time = time.time()

        cv2.imshow("Detected Shapes", frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    
    # Close connection when done
    ardiuno_compound.close()

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
