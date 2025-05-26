#!/usr/bin/env python3

import cv2
import depthai as dai
import numpy as np
import sys
import math
import time


from GNC.Control_Core import motor_core
from API.Servos.ardiuno_compound import ArdiunoCompound


# === Calibration Constants ===
TIME_DELAY = 5
LAUNCH_DISTANCE_THRESHOLD = 1.0  # in meters

# HSV Ranges for Black and White Object Detection
LOWER_BLACK = np.array([0, 0, 0])
UPPER_BLACK = np.array([120, 255,   2])
LOWER_WHITE = np.array([86,  6,  16])
UPPER_WHITE = np.array([140,  25,  40]) #100  10 234
KERNEL = np.ones((5, 5), np.uint8)

# === Image Processing ===

def process_frame(frame):
    """Convert BGR frame to HSV and apply color masks for black and white regions."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask_black = cv2.inRange(hsv, LOWER_BLACK, UPPER_BLACK)
    mask_white = cv2.inRange(hsv, LOWER_WHITE, UPPER_WHITE)

    # Noise reduction
    mask_black = cv2.morphologyEx(mask_black, cv2.MORPH_CLOSE, KERNEL)
    mask_black = cv2.morphologyEx(mask_black, cv2.MORPH_OPEN, KERNEL)
    mask_white = cv2.morphologyEx(mask_white, cv2.MORPH_CLOSE, KERNEL)
    mask_white = cv2.morphologyEx(mask_white, cv2.MORPH_OPEN, KERNEL)

    return mask_black, mask_white

def find_contours(mask, frame, shape_name='black'):
    """Find black crosses or white squares in the mask image."""
    centroids = []
    info = []
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 1000:
            approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
            M = cv2.moments(cnt)

            if M['m00'] == 0:
                continue

            c_x = int(M['m10'] / M['m00'])
            c_y = int(M['m01'] / M['m00'])
            x, y, w, h = cv2.boundingRect(cnt)

            if shape_name == 'black' and len(approx) == 12:
                # Draw and annotate black cross
                cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(frame, 'Black Cross', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.circle(frame, (c_x, c_y), 8, (0, 128, 0), -1)

                centroids.append((c_x, c_y))
                info.append(((c_x, c_y), w, h))

            elif shape_name == 'white' and len(approx) >= 4:
                # Draw and annotate white square
                cv2.drawContours(frame, [cnt], -1, (0, 255, 255), 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 87, 51), 2)
                cv2.putText(frame, 'White Square', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                cv2.circle(frame, (c_x, c_y), 8, (191, 64, 191), -1)

                centroids.append((c_x, c_y))
                info.append(((c_x, c_y), w, h))


    return (centroids, info)

def find_closest_match(black_info, white_centroids):
    """Find the closest white centroid to a black cross."""
    min_distance = float('inf')
    closest = None
    for (bc, bw, bh) in black_info:
        for wc in white_centroids:
            dist = math.hypot(bc[0] - wc[0], bc[1] - wc[1])
            if dist < min_distance:
                min_distance = dist
                closest = (bc, bw, bh)
    return closest

def launch_ardiuno(ardiuno_compound):
    """Trigger the Arduino launch sequence."""
    ardiuno_compound.send_command("g")
    time.sleep(0.5)
    ardiuno_compound.send_command("A")
    time.sleep(10)

def handle_distance_action(black_dist_m, x, y, frame):
    global ball_launched, motor_move, motor, ardiuno_compound

    if black_dist_m > 1.0:
        if motor_move:
            motor.surge(0.5)
    elif black_dist_m <= 1.0 and ball_launched:
        print("ball launched")
        launch_ardiuno(ardiuno_compound)
        ball_launched = False
        return True  # Indicates launch occurred
    return False

def process_target_match(match, frame, depth_frame, w_ratio, h_ratio):
    closest_black, closest_w, closest_h = match
    x, y = closest_black

    x1 = int((x - closest_w // 2) * w_ratio)
    y1 = int((y - closest_h // 2) * h_ratio)
    x2 = int((x + closest_w // 2) * w_ratio)
    y2 = int((y + closest_h // 2) * h_ratio)

    x1 = max(0, min(depth_frame.shape[1] - 1, x1))
    y1 = max(0, min(depth_frame.shape[0] - 1, y1))
    x2 = max(0, min(depth_frame.shape[1] - 1, x2))
    y2 = max(0, min(depth_frame.shape[0] - 1, y2))

    mask_shape = np.zeros(depth_frame.shape, dtype=np.uint8)
    cv2.rectangle(mask_shape, (x1, y1), (x2, y2), 255, -1)
    masked_depth = np.where(mask_shape == 255, depth_frame, np.nan)
    valid_depths = masked_depth[~np.isnan(masked_depth)]

    if valid_depths.size > 0:
        black_dist_m = np.nanmean(valid_depths) / 1000.0
        cv2.putText(frame, f'{black_dist_m:.2f}m', (x + 10, y + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (245, 66, 230), 3)
        return handle_distance_action(black_dist_m, x, y, frame)
    return False
    
def process_fallback_black_targets(black_info, frame, depth_frame, w_ratio, h_ratio):
    for (c_black, w, h) in black_info:
        x, y = c_black

        x1 = int((x - w // 2) * w_ratio)
        y1 = int((y - h // 2) * h_ratio)
        x2 = int((x + w // 2) * w_ratio)
        y2 = int((y + h // 2) * h_ratio)

        x1 = max(0, min(depth_frame.shape[1] - 1, x1))
        y1 = max(0, min(depth_frame.shape[0] - 1, y1))
        x2 = max(0, min(depth_frame.shape[1] - 1, x2))
        y2 = max(0, min(depth_frame.shape[0] - 1, y2))

        mask_shape = np.zeros(depth_frame.shape, dtype=np.uint8)
        cv2.rectangle(mask_shape, (x1, y1), (x2, y2), 255, -1)
        masked_depth = np.where(mask_shape == 255, depth_frame, np.nan)
        valid_depths = masked_depth[~np.isnan(masked_depth)]

        if valid_depths.size > 0:
            black_dist_m = np.nanmean(valid_depths) / 1000.0
            cv2.putText(frame, f'{black_dist_m:.2f}m', (x + 10, y + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (245, 66, 230), 3)
            if handle_distance_action(black_dist_m, x, y, frame):
                return True
    return False

def annotate_white_squares(frame, white_info, depth_frame, w_ratio, h_ratio):
    for ((wc_x, wc_y), w, h) in white_info:
        x1 = int((wc_x - w // 2) * w_ratio)
        y1 = int((wc_y - h // 2) * h_ratio)
        x2 = int((wc_x + w // 2) * w_ratio)
        y2 = int((wc_y + h // 2) * h_ratio)

        x1 = max(0, min(depth_frame.shape[1] - 1, x1))
        y1 = max(0, min(depth_frame.shape[0] - 1, y1))
        x2 = max(0, min(depth_frame.shape[1] - 1, x2))
        y2 = max(0, min(depth_frame.shape[0] - 1, y2))

        mask_white_region = np.zeros(depth_frame.shape, dtype=np.uint8)
        cv2.rectangle(mask_white_region, (x1, y1), (x2, y2), 255, -1)
        white_masked_depth = np.where(mask_white_region == 255, depth_frame, np.nan)
        white_valid = white_masked_depth[~np.isnan(white_masked_depth)]

        if white_valid.size > 0:
            white_dist_m = np.nanmean(white_valid) / 1000.0
            cv2.putText(frame, f'{white_dist_m:.2f}m', (wc_x + 10, wc_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)


ball_launched = False
motor_move = True
LAUNCH_DISTANCE_THRESHOLD = 1.0  # in meters

# Stereo depth settings
EXTENDED_DISPARITY = False  # Doubles disparity range
SUBPIXEL = True  # Improves accuracy
LR_CHECK = True  # Handles occlusions better

ardiuno_compound = ArdiunoCompound(port="/dev/ttyACM3")
motor = motor_core.MotorCore("/dev/ttyACM2")

# Create pipeline
pipeline = dai.Pipeline()

# Create camera nodes
left_cam = pipeline.create(dai.node.ColorCamera)
right_cam = pipeline.create(dai.node.ColorCamera)
stereo = pipeline.create(dai.node.StereoDepth)

# Create output nodes
xout_left = pipeline.create(dai.node.XLinkOut)
xout_right = pipeline.create(dai.node.XLinkOut)
xout = pipeline.create(dai.node.XLinkOut)
xout_depth = pipeline.create(dai.node.XLinkOut)

# Set stream name
xout_left.setStreamName("left")
xout_right.setStreamName("right")
xout.setStreamName("disparity")
xout_depth.setStreamName("depth")

# Configure left camera
left_cam.setBoardSocket(dai.CameraBoardSocket.CAM_A)
left_cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1200_P)
left_cam.setCamera("left")
left_cam.setIspScale(2, 3)

# Configure right camera
right_cam.setBoardSocket(dai.CameraBoardSocket.CAM_B)
right_cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1200_P)
right_cam.setCamera("right")
right_cam.setIspScale(2, 3)

# Configure stereo depth node
stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.DEFAULT)
stereo.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
stereo.setLeftRightCheck(LR_CHECK)
stereo.setExtendedDisparity(EXTENDED_DISPARITY)
stereo.setSubpixel(SUBPIXEL)

# Link nodes for stereo
left_cam.isp.link(stereo.left)
right_cam.isp.link(stereo.right)
stereo.depth.link(xout.input)

# Link nodes for individual camera 
left_cam.isp.link(xout_left.input)
#right_cam.isp.link(xout_right.input)

# Mouse callback function to display depth at hovered pixel
#def on_mouse(event, x, y, flags, param):
#    if event == cv2.EVENT_MOUSEMOVE:
#        depth_value = depth_map[y, x] if 0 <= y < depth_map.shape[0] and 0 <= x < depth_map.shape[1] else None
#        disparity_value = disparity_map[y, x] if 0 <= y < disparity_map.shape[0] and 0 <= x < disparity_map.shape[1] else None
#        if depth_value is not None:
#            print(f"Disparity at ({x}, {y}): {disparity_value/1000:.2f} meter | Depth: {depth_value:.2f} cm", end="\r")


try:
    with dai.Device(pipeline) as device:
        # Retrieve camera calibration data
        intrinsic_dataB = device.readCalibration().getCameraIntrinsics(dai.CameraBoardSocket.CAM_B)
        intrinsic_dataA = device.readCalibration().getCameraIntrinsics(dai.CameraBoardSocket.CAM_A)
        focal_lengthB = intrinsic_dataB[0][0]
        focal_lengthA = intrinsic_dataA[0][0]

        print("Cam B focal length in pixels:", focal_lengthA)
        print("Cam C focal length in pixels:", focal_lengthA)
        left_q = device.getOutputQueue(name="left", maxSize=4, blocking=False)
        #right_q = device.getOutputQueue(name="right", maxSize=4, blocking=False)
        q = device.getOutputQueue(name="disparity", maxSize=4, blocking=False)

        cv2.namedWindow("raw disparity")
        #cv2.setMouseCallback("raw disparity", on_mouse)

        while True:
            try:
                # display original image of two cameras
                cv2.imshow("Left Camera", left_q.get().getCvFrame())
                #cv2.imshow("Right Camera", right_q.get().getCvFrame())
                
                # getting color frame
                frame = left_q.get().getCvFrame()
                
                # apply detections
                mask_black, mask_white = process_frame(frame)
                
                # finding centorids and h and width of detections
                black_centroids, black_info = find_contours(mask_black, frame, 'black')
                white_centroids, white_info = find_contours(mask_white, frame, 'white')
                print(f"White boxes detected: {len(white_info)}")
                
                # Get disparity frame
                in_disparity = q.get()
                depth_in_meters = in_disparity.getFrame().astype(np.float32) / 1000.0
                depth_frame = depth_in_meters
                #depth_in_meters = in_disparity.getCvFrame()

                
                # === Compute scale ratios from frame to depth_frame ===
                h_ratio = depth_frame.shape[0] / frame.shape[0]
                w_ratio = depth_frame.shape[1] / frame.shape[1]

                # Always annotate white squares
                annotate_white_squares(frame, white_info, depth_frame, w_ratio, h_ratio)

                # Main logic: match if white exists, fallback if not
                if white_info:
                    match = find_closest_match(black_info, white_centroids)
                    if match:
                        if process_target_match(match, frame, depth_frame, w_ratio, h_ratio):
                            break
                else:
                    if process_fallback_black_targets(black_info, frame, depth_frame, w_ratio, h_ratio):
                        break



                #The return value in the disparity map doesn't make sense, when you hover over the disparity map window, the disparity is 
                # too large(2000 as the return), while the real camera disparity of that object is only 50
                # TODO: Find the meaning of the disparity map return, and concert it to what we need, in pixel
                max_disparity = stereo.initialConfig.getMaxDisparity()
                normalized_disparity = (depth_in_meters * (255 / max_disparity)).astype(np.uint8)
                #depth_in_meters = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)
                disp_bgr = cv2.cvtColor(normalized_disparity, cv2.COLOR_GRAY2BGR)

                # Draw bounding boxes from white square detections
                # Get scaling factors from original frame to disparity map
                h_ratio = disp_bgr.shape[0] / frame.shape[0]
                w_ratio = disp_bgr.shape[1] / frame.shape[1]
                
                # drawing white bounding boxes
                for ((wc_x, wc_y), w, h) in white_info:
                    x1 = int((wc_x - w // 2) * w_ratio)
                    y1 = int((wc_y - h // 2) * h_ratio)
                    x2 = int((wc_x + w // 2) * w_ratio)
                    y2 = int((wc_y + h // 2) * h_ratio)

                    # Clamp to image bounds
                    x1 = max(0, min(disp_bgr.shape[1] - 1, x1))
                    y1 = max(0, min(disp_bgr.shape[0] - 1, y1))
                    x2 = max(0, min(disp_bgr.shape[1] - 1, x2))
                    y2 = max(0, min(disp_bgr.shape[0] - 1, y2))

                    cv2.rectangle(disp_bgr, (x1, y1), (x2, y2), (0, 255, 255), 2)
                    
                # drawing black bounding boxes
                for ((wc_x, wc_y), w, h) in black_info:
                    x1 = int((wc_x - w // 2) * w_ratio)
                    y1 = int((wc_y - h // 2) * h_ratio)
                    x2 = int((wc_x + w // 2) * w_ratio)
                    y2 = int((wc_y + h // 2) * h_ratio)

                    # Clamp to image bounds
                    x1 = max(0, min(disp_bgr.shape[1] - 1, x1))
                    y1 = max(0, min(disp_bgr.shape[0] - 1, y1))
                    x2 = max(0, min(disp_bgr.shape[1] - 1, x2))
                    y2 = max(0, min(disp_bgr.shape[0] - 1, y2))

                    cv2.rectangle(disp_bgr, (x1, y1), (x2, y2), (245, 66, 230), 2)

                cv2.imshow("raw disparity", disp_bgr)
                cv2.imshow("w bounding boxes", frame)

                #cv2.imshow("Detected Shapes", preview_frame)
                #cv2.imshow("raw disparity", normalized_disparity)
                
                # Compute depth map
                depth_map = depth_in_meters  #(focal_lengthA * 15) / np.maximum(depth_in_meters, 0.001) 
                depth_map = np.clip(depth_map, 0, 3000)  # Limit depth to 30m
                
                if cv2.waitKey(1) == ord('q'):
                    break
            except Exception as e:
                print(f"Error processing frame: {e}")
                break

except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)

finally:
    ardiuno_compound.close()
    cv2.destroyAllWindows()