#!/usr/bin/env python3

import cv2
import depthai as dai
import numpy as np
import time
import math
from API.Servos.mini_maestro import MiniMaestro
from API.Servos.ardiuno_compound import ArdiunoCompound
from GNC.Control_Core import motor_core

# === Calibration Constants ===
TIME_DELAY = 5
LAUNCH_DISTANCE_THRESHOLD = 1.0  # in meters

LOWER_BLACK = np.array([0, 0, 0])
UPPER_BLACK = np.array([180, 80, 100])
LOWER_WHITE = np.array([0, 0, 170])
UPPER_WHITE = np.array([180, 60, 255])
KERNEL = np.ones((5, 5), np.uint8)


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


def launch_ardiuno(ardiuno_compound):
    ardiuno_compound.send_command("g")
    time.sleep(0.5)
    ardiuno_compound.send_command("A")
    time.sleep(10)


def main():
    # Create pipeline
    pipeline = dai.Pipeline()

    # Color camera for visual processing
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
    cam_rgb.setInterleaved(False)

    xout_rgb = pipeline.create(dai.node.XLinkOut)
    xout_rgb.setStreamName("color")
    cam_rgb.video.link(xout_rgb.input)

    # Mono cameras for depth (resolution ≤ 1280 width)
    mono_left = pipeline.create(dai.node.MonoCamera)
    mono_right = pipeline.create(dai.node.MonoCamera)
    stereo = pipeline.create(dai.node.StereoDepth)

    mono_left.setBoardSocket(dai.CameraBoardSocket.CAM_B)
    mono_right.setBoardSocket(dai.CameraBoardSocket.CAM_C)
    mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)

    stereo.setLeftRightCheck(True)
    stereo.setSubpixel(True)
    stereo.setExtendedDisparity(False)
    stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.DEFAULT)

    mono_left.out.link(stereo.left)
    mono_right.out.link(stereo.right)

    xout_depth = pipeline.create(dai.node.XLinkOut)
    xout_depth.setStreamName("depth")
    stereo.depth.link(xout_depth.input)

    # Start pipeline
    with dai.Device(pipeline) as device:
        color_queue = device.getOutputQueue(name="color", maxSize=4, blocking=False)
        depth_queue = device.getOutputQueue(name="depth", maxSize=4, blocking=False)

        ardiuno_compound = ArdiunoCompound(port="/dev/ttyACM2")
        maestro = MiniMaestro(port="/dev/ttyACM0")
        motor = motor_core.MotorCore("/dev/ttyACM0")

        motor_move = True
        ball_launched = True
        last_shot_time = time.time()

        while True:
            frame = color_queue.get().getCvFrame()
            depth_frame = depth_queue.get().getFrame().astype(np.float32)
            depth_frame[depth_frame == 0] = np.nan  # Mask out invalid depth

            mask_black, mask_white = process_frame(frame)
            black_centroids, black_info = find_contours(mask_black, frame, 'black')
            white_centroids, _ = find_contours(mask_white, frame, 'white')

            match = find_closest_match(black_info, white_centroids)
            if match:
                closest_black, closest_w, closest_h = match
                x, y = closest_black

                if 0 <= y < depth_frame.shape[0] and 0 <= x < depth_frame.shape[1]:
                    distance_mm = depth_frame[int(y), int(x)]
                    distance_m = distance_mm / 1000.0  # Convert mm to meters

                    if motor_move:
                        motor.surge(0.5)

                    cv2.circle(frame, (x, y), 15, (0, 0, 255), 3)
                    cv2.putText(frame, f'{closest_w}x{closest_h}px, {distance_m:.2f}m',
                                (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                    print(f"Target at {distance_m:.2f} meters")

                    if ball_launched and distance_m <= LAUNCH_DISTANCE_THRESHOLD and time.time() - last_shot_time >= TIME_DELAY:
                        if motor_move:
                            motor.stay()
                        launch_ardiuno(ardiuno_compound)
                        print("Ball launched!")
                        last_shot_time = time.time()
                        ball_launched = False
                        break

            cv2.imshow("Detected Shapes", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        ardiuno_compound.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
