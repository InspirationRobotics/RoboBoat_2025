#!/usr/bin/env python3

import cv2
import depthai as dai
import numpy as np
import sys
import time
from ultralytics import YOLO

# === Load YOLOv8 model ===
model = YOLO("best (2).pt")  # Ensure the model is in the correct path

# === Stereo depth settings ===
EXTENDED_DISPARITY = False
SUBPIXEL = True
LR_CHECK = True

# === Create pipeline ===
pipeline = dai.Pipeline()

# Create camera nodes
left_cam = pipeline.create(dai.node.ColorCamera)
right_cam = pipeline.create(dai.node.ColorCamera)
stereo = pipeline.create(dai.node.StereoDepth)

# Create output nodes
xout_left = pipeline.create(dai.node.XLinkOut)
xout = pipeline.create(dai.node.XLinkOut)

# Set stream names
xout_left.setStreamName("left")
xout.setStreamName("disparity")

# Configure left camera
left_cam.setBoardSocket(dai.CameraBoardSocket.CAM_A)
left_cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_720_P)
left_cam.setIspScale(2, 3)

# Configure right camera
right_cam.setBoardSocket(dai.CameraBoardSocket.CAM_B)
right_cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_720_P)
right_cam.setIspScale(2, 3)

# Stereo depth configuration
stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.DEFAULT)
stereo.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
stereo.setLeftRightCheck(LR_CHECK)
stereo.setExtendedDisparity(EXTENDED_DISPARITY)
stereo.setSubpixel(SUBPIXEL)

# Link cameras to stereo node
left_cam.isp.link(stereo.left)
right_cam.isp.link(stereo.right)
stereo.depth.link(xout.input)

# Link left camera to output
left_cam.isp.link(xout_left.input)

# === Start device ===
try:
    with dai.Device(pipeline) as device:
        # Retrieve camera calibration data
        intrinsics = device.readCalibration().getCameraIntrinsics(dai.CameraBoardSocket.CAM_A)
        focal_length_px = intrinsics[0][0]
        print("Focal length (pixels):", focal_length_px)

        left_q = device.getOutputQueue(name="left", maxSize=4, blocking=False)
        disparity_q = device.getOutputQueue(name="disparity", maxSize=4, blocking=False)

        cv2.namedWindow("raw disparity")

        while True:
            frame = left_q.get().getCvFrame()
            disparity_data = disparity_q.get()
            disparity_map = disparity_data.getCvFrame().astype(np.float32)
            depth_frame = disparity_map.copy()

            # === Run YOLO on the frame ===
            results = model(frame)[0]
            cross_info = []

            for det in results.boxes.data:
                x1, y1, x2, y2, conf, cls = det.tolist()
                label = results.names[int(cls)]

                if label.lower() == "cross":
                    c_x = int((x1 + x2) / 2)
                    c_y = int((y1 + y2) / 2)
                    w = int(x2 - x1)
                    h = int(y2 - y1)

                    cross_info.append(((c_x, c_y), w, h))
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.putText(frame, 'Cross', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.circle(frame, (c_x, c_y), 5, (0, 255, 0), -1)

            # === Estimate depth for each detected cross ===
            h_ratio = depth_frame.shape[0] / frame.shape[0]
            w_ratio = depth_frame.shape[1] / frame.shape[1]

            for ((x, y), w, h) in cross_info:
                x1 = int((x - w // 2) * w_ratio)
                y1 = int((y - h // 2) * h_ratio)
                x2 = int((x + w // 2) * w_ratio)
                y2 = int((y + h // 2) * h_ratio)

                x1 = max(0, min(depth_frame.shape[1] - 1, x1))
                y1 = max(0, min(depth_frame.shape[0] - 1, y1))
                x2 = max(0, min(depth_frame.shape[1] - 1, x2))
                y2 = max(0, min(depth_frame.shape[0] - 1, y2))

                mask = np.zeros(depth_frame.shape, dtype=np.uint8)
                cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
                masked_depth = np.where(mask == 255, depth_frame, np.nan)
                valid_depths = masked_depth[~np.isnan(masked_depth)]

                if valid_depths.size > 0:
                    depth_m = np.nanmean(valid_depths) / 1000.0
                    cv2.putText(frame, f'{depth_m:.2f}m', (x + 10, y + 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

            # === Normalize and display disparity ===
            max_disp = stereo.initialConfig.getMaxDisparity()
            norm_disp = (disparity_map * (255.0 / max_disp)).astype(np.uint8)
            disp_bgr = cv2.cvtColor(norm_disp, cv2.COLOR_GRAY2BGR)

            # Draw boxes in disparity view
            for ((x, y), w, h) in cross_info:
                x1 = int((x - w // 2) * w_ratio)
                y1 = int((y - h // 2) * h_ratio)
                x2 = int((x + w // 2) * w_ratio)
                y2 = int((y + h // 2) * h_ratio)
                x1 = max(0, min(disp_bgr.shape[1] - 1, x1))
                y1 = max(0, min(disp_bgr.shape[0] - 1, y1))
                x2 = max(0, min(disp_bgr.shape[1] - 1, x2))
                y2 = max(0, min(disp_bgr.shape[0] - 1, y2))
                cv2.rectangle(disp_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # === Display frames ===
            cv2.imshow("raw disparity", disp_bgr)
            cv2.imshow("Detections", frame)

            if cv2.waitKey(1) == ord('q'):
                break

except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)

finally:
    cv2.destroyAllWindows()
