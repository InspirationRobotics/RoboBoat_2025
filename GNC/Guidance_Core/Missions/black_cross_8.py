#!/usr/bin/env python3

import cv2
import depthai as dai
import numpy as np
import sys
from ultralytics import YOLO

model = YOLO("best (2).pt")

# === Stereo depth settings ===
EXTENDED_DISPARITY = False
SUBPIXEL = True
LR_CHECK = True

pipeline = dai.Pipeline()

# Create mono cameras
left = pipeline.create(dai.node.MonoCamera)
right = pipeline.create(dai.node.MonoCamera)
left.setBoardSocket(dai.CameraBoardSocket.CAM_B)
right.setBoardSocket(dai.CameraBoardSocket.CAM_C)
left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_1200_P)
right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_1200_P)

# Resize using ImageManip to 1280x720
left_manip = pipeline.create(dai.node.ImageManip)
right_manip = pipeline.create(dai.node.ImageManip)
left_manip.initialConfig.setResize(1280, 720)
right_manip.initialConfig.setResize(1280, 720)
left.out.link(left_manip.inputImage)
right.out.link(right_manip.inputImage)

# Stereo depth node
stereo = pipeline.create(dai.node.StereoDepth)
stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.DEFAULT)
stereo.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
stereo.setLeftRightCheck(LR_CHECK)
stereo.setExtendedDisparity(EXTENDED_DISPARITY)
stereo.setSubpixel(SUBPIXEL)

left_manip.out.link(stereo.left)
right_manip.out.link(stereo.right)

# Output streams
xout_left = pipeline.create(dai.node.XLinkOut)
xout_depth = pipeline.create(dai.node.XLinkOut)
xout_left.setStreamName("left")
xout_depth.setStreamName("disparity")
left_manip.out.link(xout_left.input)
stereo.depth.link(xout_depth.input)

try:
    with dai.Device(pipeline) as device:
        intrinsics = device.readCalibration().getCameraIntrinsics(dai.CameraBoardSocket.CAM_B)
        focal_length_px = intrinsics[0][0]
        print("Focal length (pixels):", focal_length_px)

        left_q = device.getOutputQueue("left", maxSize=4, blocking=False)
        disparity_q = device.getOutputQueue("disparity", maxSize=4, blocking=False)

        max_disp = stereo.initialConfig.getMaxDisparity()
        cv2.namedWindow("Disparity")
        cv2.namedWindow("Detections")

        while True:
            frame = left_q.get().getCvFrame()
            disparity_map = disparity_q.get().getCvFrame().astype(np.float32)
            depth_frame = disparity_map.copy()

            h_frame, w_frame = frame.shape[:2]
            h_disp, w_disp = depth_frame.shape[:2]
            h_ratio, w_ratio = h_disp / h_frame, w_disp / w_frame

            results = model(frame)[0]
            cross_info = []

            for det in results.boxes.data:
                x1, y1, x2, y2, conf, cls = det.tolist()
                if conf < 0.4:
                    continue
                label = results.names[int(cls)]
                if label.lower() == "cross":
                    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                    c_x, c_y = (x1 + x2) // 2, (y1 + y2) // 2
                    w, h = x2 - x1, y2 - y1
                    cross_info.append(((c_x, c_y), w, h))
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, 'Cross', (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.circle(frame, (c_x, c_y), 5, (0, 255, 0), -1)

            for ((x, y), w, h) in cross_info:
                x1 = max(0, min(w_disp - 1, int((x - w // 2) * w_ratio)))
                y1 = max(0, min(h_disp - 1, int((y - h // 2) * h_ratio)))
                x2 = max(0, min(w_disp - 1, int((x + w // 2) * w_ratio)))
                y2 = max(0, min(h_disp - 1, int((y + h // 2) * h_ratio)))

                roi = depth_frame[y1:y2, x1:x2]
                valid_depths = roi[roi > 0]

                if valid_depths.size > 0:
                    depth_m = np.mean(valid_depths) / 1000.0
                    cv2.putText(frame, f'{depth_m:.2f}m', (x + 10, y + 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

            norm_disp = (disparity_map * (255.0 / max_disp)).astype(np.uint8)
            disp_bgr = cv2.cvtColor(norm_disp, cv2.COLOR_GRAY2BGR)

            for ((x, y), w, h) in cross_info:
                x1 = max(0, min(w_disp - 1, int((x - w // 2) * w_ratio)))
                y1 = max(0, min(h_disp - 1, int((y - h // 2) * h_ratio)))
                x2 = max(0, min(w_disp - 1, int((x + w // 2) * w_ratio)))
                y2 = max(0, min(h_disp - 1, int((y + h // 2) * h_ratio)))
                cv2.rectangle(disp_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.imshow("Disparity", disp_bgr)
            cv2.imshow("Detections", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)

finally:
    cv2.destroyAllWindows()
