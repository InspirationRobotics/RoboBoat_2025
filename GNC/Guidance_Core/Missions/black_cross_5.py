import cv2
import depthai as dai
import numpy as np
import time
import math
from API.Servos.mini_maestro import MiniMaestro
from API.Servos.ardiuno_compound import ArdiunoCompound
from GNC.Control_Core import motor_core
import csv

# === Calibration Constants ===
TIME_DELAY = 5
LAUNCH_DISTANCE_THRESHOLD = 1.0  # in meters

# HSV Ranges for Black and White Object Detection
LOWER_BLACK = np.array([0, 0, 0])
UPPER_BLACK = np.array([80, 255, 76])
LOWER_WHITE = np.array([0, 0, 170])
UPPER_WHITE = np.array([105, 17, 210])
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

    return (centroids, info) if shape_name == 'black' else (centroids, [])

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

# === Main Execution ===

def main():
    # === DepthAI Pipeline Configuration ===
    pipeline = dai.Pipeline()

    # Color camera
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
    cam_rgb.setInterleaved(False)

    # Stereo cameras
    mono_left = pipeline.create(dai.node.MonoCamera)
    mono_right = pipeline.create(dai.node.MonoCamera)
    stereo = pipeline.create(dai.node.StereoDepth)

    mono_left.setBoardSocket(dai.CameraBoardSocket.CAM_B)
    mono_right.setBoardSocket(dai.CameraBoardSocket.CAM_C)
    mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)


    # Stereo config
    stereo.setLeftRightCheck(True)
    stereo.setSubpixel(True)
    stereo.setExtendedDisparity(True)
    stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.DEFAULT)

    # Resize mono images
    manip_left = pipeline.create(dai.node.ImageManip)
    manip_right = pipeline.create(dai.node.ImageManip)
    manip_left.initialConfig.setResize(1280, 720)
    manip_right.initialConfig.setResize(1280, 720)
    mono_left.out.link(manip_left.inputImage)
    mono_right.out.link(manip_right.inputImage)
    manip_left.out.link(stereo.left)
    manip_right.out.link(stereo.right)

    # Output nodes
    xout_rgb = pipeline.create(dai.node.XLinkOut)
    xout_rgb.setStreamName("color")
    cam_rgb.video.link(xout_rgb.input)

    xout_depth = pipeline.create(dai.node.XLinkOut)
    xout_depth.setStreamName("depth")
    stereo.depth.link(xout_depth.input)

    xout_disp = pipeline.create(dai.node.XLinkOut)
    xout_disp.setStreamName("disparity")
    stereo.disparity.link(xout_disp.input)

    # Create display windows
    cv2.namedWindow("Detected Shapes")
    cv2.namedWindow("raw disparity")

    with dai.Device(pipeline) as device:
        color_queue = device.getOutputQueue(name="color", maxSize=4, blocking=False)
        depth_queue = device.getOutputQueue(name="depth", maxSize=4, blocking=False)
        disp_queue = device.getOutputQueue(name="disparity", maxSize=4, blocking=False)

        ardiuno_compound = ArdiunoCompound(port="/dev/ttyACM2")
        maestro = MiniMaestro(port="/dev/ttyACM0")
        motor = motor_core.MotorCore("/dev/ttyACM0")

        motor_move = False
        ball_launched = False
        last_shot_time = time.time()

        while True:
            # Get latest frames
            frame = color_queue.get().getCvFrame()
            depth_frame = depth_queue.get().getFrame().astype(np.float32)
            disparity_map = disp_queue.get().getCvFrame()
            depth_frame[depth_frame == 0] = np.nan

            # Process detections
            mask_black, mask_white = process_frame(frame)
            black_centroids, black_info = find_contours(mask_black, frame, 'black')
            white_centroids, _ = find_contours(mask_white, frame, 'white')
            
            # Target matching
            match = find_closest_match(black_info, white_centroids)
            if match:
                closest_black, closest_w, closest_h = match
                x, y = closest_black
                
                if False: # set to true if want to save depth mask
                    print(depth_frame)

                    filename = 'data.csv'

                    with open(filename, 'w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerows(depth_frame)
                        break 
                    
                # Define a mask for the black cross region
                mask_shape = np.zeros(depth_frame.shape, dtype=np.uint8)
                cv2.rectangle(mask_shape, (x - closest_w // 2, y - closest_h // 2),
                              (x + closest_w // 2, y + closest_h // 2), 255, -1)

                # Mask depth values
                masked_depth = np.where(mask_shape == 255, depth_frame, np.nan)
                valid_depths = masked_depth[~np.isnan(masked_depth)]
                
                print(valid_depths)

                if valid_depths.size > 0:
                    distance_m = np.nanmean(valid_depths) / 1000.0  # mm to m
                else:
                    distance_m = float('inf')  # fallback if no valid depth


                    if motor_move:
                        motor.surge(0.5)

                    cv2.circle(frame, (x, y), 15, (0, 0, 255), 3)
                    cv2.putText(frame, f'{closest_w}x{closest_h}px, {distance_m:.2f}m',
                                (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                    if ball_launched and distance_m <= LAUNCH_DISTANCE_THRESHOLD and time.time() - last_shot_time >= TIME_DELAY:
                        if motor_move:
                            motor.stay()
                        launch_ardiuno(ardiuno_compound)
                        print("Ball launched!")
                        last_shot_time = time.time()
                        ball_launched = False

            # Resize and display
            preview_frame = cv2.resize(frame, (960, 540))

            # Normalize disparity for visualization
            max_disparity = stereo.initialConfig.getMaxDisparity()
            normalized_disparity = (disparity_map * (255 / max_disparity)).astype(np.uint8)
            cv2.imshow("raw disparity", normalized_disparity)
            cv2.imshow("Detected Shapes", preview_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        ardiuno_compound.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
