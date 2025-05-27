import cv2
import numpy as np
import math
from API.Servos.mini_maestro import MiniMaestro
from API.Servos.ardiuno_compound import ArdiunoCompound
from GNC.Control_Core  import motor_core # for the motor

import time

# === Calibration Constants ===
REAL_WIDTH_METERS = 0.4699 #18.5 inches accross
FOCAL_LENGTH = 588.3843844
TIME_DELAY = 5
LAUNCH_DISTANCE_THRESHOLD = 1.25

# day time
LOWER_BLACK = np.array([0, 0, 0])
UPPER_BLACK = np.array([255, 255, 100])#([180, 80, 100])
LOWER_WHITE = np.array([0, 0, 170])
UPPER_WHITE = np.array([15, 15, 255])#([180, 60, 255])

# night time hello
#LOWER_BLACK = np.array([0, 0, 0])
#UPPER_BLACK = np.array([120, 255,   2])
#LOWER_WHITE = np.array([0, 0, 5])
#UPPER_WHITE = np.array([255, 17, 255]) #100  10 234
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
    return (REAL_WIDTH_METERS * FOCAL_LENGTH) / pixel_width


def launch(maestro):
    maestro.set_pwm(0, 1800)
    time.sleep(2)
    maestro.set_pwm(0, 1500)

def launch_ardiuno(ardiuno_compound):
    # Send simple character command
    ardiuno_compound.send_command("g")  # Will now send as bytes: b'g'
    time.sleep(0.5)
    ardiuno_compound.send_command("A")  # reloading
    time.sleep(10)


def main():
        # Change port based on your system (e.g., "COM3" on Windows, "/dev/ttyUSB0" on Linux/Mac)
    #ardiuno_compound = ArdiunoCompound(port="/dev/ttyACM2")
    #
    #maestro = MiniMaestro(port="/dev/ttyACM0")
    
    ardiuno_compound = ArdiunoCompound(port="/dev/ttyACM3")
    motor = motor_core.MotorCore("/dev/ttyACM2")
    cap = init_camera()
    last_shot_time = time.time()
    ball_launched = True # this is to only allow one ball launch / chooses if we launch a ball
    #motor      = motor_core.MotorCore("/dev/ttyACM0") # load with default port "/dev/ttyACM0"
    motor_move = True # to control if we move with motors
    
    last_x = 0
    detection_counter = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        mask_black, mask_white = process_frame(frame)
        black_centroids, black_info = find_contours(mask_black, frame, 'black')
        white_centroids, _ = find_contours(mask_white, frame, 'white')

        # for front end and back end variables controlling movement
        frame_height, frame_width = frame.shape[:2]
        left_bound = frame_width // 5
        right_bound = 4*frame_width // 5
        

        match = find_closest_match(black_info, white_centroids)
        if match:
            frame_height, frame_width = frame.shape[:2]
            closest_black, closest_w, closest_h = match
            x, y = closest_black


            last_x = x # stores the last detection
            # if can see the cross move forward
            if motor_move:
                if x < left_bound:
                    cv2.putText(frame, 'left', (50, 50),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                    print("Turning LEFT to center target...")
                    motor.veer(0.2,-0.2)  # Negative = counterclockwise (left)
                    #         # NOTE: We want positive to be left, negative to be right.    def veer(self, magnitudeF, magnitudeB):
                    """ 
                    Move forward and yaw at the same time. Front two motor moves forward, back two motor yaw
                    Arguments:
                        magnitudeF : magnitude for front motors
                        magnitudeB : magnitude for back motors

                    Usage:
                        Positive magnitudeF is forward
                        Positive magnitudeB is clockwise
                    """

                elif x > right_bound:
                    cv2.putText(frame, 'right', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                    print("Turning RIGHT to center target...")
                    motor.veer(0.2,0.2)  # Positive = clockwise (right)

                else:
                    cv2.putText(frame, 'center', (50, 50),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                    print("Target centered — moving forward...")
                    motor.surge(0.2)

                
            # estimating distance
            closest_black, closest_w, closest_h = match
            distance = estimate_distance(closest_w)

            # front end user interface
            cv2.circle(frame, closest_black, 15, (0, 0, 255), 3)
            cv2.putText(frame, f'{closest_w}x{closest_h}px, {distance:.1f}m',
                        (closest_black[0] + 10, closest_black[1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            print(f"Target at {distance:.2f} meters")
            if ball_launched:
                if distance <= LAUNCH_DISTANCE_THRESHOLD and time.time() - last_shot_time >= TIME_DELAY:
                    detection_counter = detection_counter + 1
                    if motor_move:
                            motor.stay()

                    if detection_counter > 20:
                        # stop moving forward
                        if motor_move:
                            motor.stay()
                        #launch(maestro)
                        launch_ardiuno(ardiuno_compound)

                        print("Ball launched!")
                        last_shot_time = time.time()
                        ball_launched = False  # break the while loop
                        break
        else:
            # no detections
            if motor_move:
                if last_x < frame_width/2:
                    # if the last detection was on left of scress cw
                    cv2.putText(frame, 'ccw', (50, 50),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                    print("no detection ccw: last x : {} < {}".format(last_x,frame_width/2))
                    motor.rotate(-.1)
                else:
                    cv2.putText(frame, 'cw', (50, 50),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                    print("no detection cw : {} < {}".format(frame_width/2,last_x))
                    motor.rotate(.1)
     
                    
        # Show HSV white mask
        cv2.imshow("HSV White Mask", mask_white)

        # Draw HSV max-color square in top-left of main window
        hsv_color = np.uint8([[[UPPER_WHITE[0], UPPER_WHITE[1], UPPER_WHITE[2]]]])
        bgr_color = cv2.cvtColor(hsv_color, cv2.COLOR_HSV2BGR)[0][0].tolist()
        cv2.rectangle(frame, (0, 0), (50, 50), bgr_color, -1)

                    
        # Draw vertical dividing lines (left 1/3 and right 2/3)
        line_color = (255, 255, 0)  # Cyan
        line_thickness = 2


        cv2.line(frame, (left_bound, 0), (left_bound, frame_height), line_color, line_thickness)
        cv2.line(frame, (right_bound, 0), (right_bound, frame_height), line_color, line_thickness)

        cv2.imshow("Detected Shapes", frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    
    # Close connection when done
    ardiuno_compound.close()

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
