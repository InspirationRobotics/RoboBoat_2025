#!/usr/bin/env python3

import cv2
import depthai as dai
import numpy as np
import sys
from ultralytics import YOLO

model = YOLO("best (2).pt")

EXTENDED_DISPARITY = False
SUBPIXEL = True
LR_CHECK = True

pipeline = dai.Pipeline()

# === Color camera for RGB ===
color_cam = pipeline.create(dai.node.ColorCamera)
color_cam.setBoardSocket(dai.CameraBoardSocket.CAM_A)
color_cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
color_cam.setIspScale(2, 3)  # Downscale to 1280x720
color_cam.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
color_cam.setInterleaved(False)

# === Mono cameras for depth ===
mono_left = pipeline.create(dai.node.MonoCamera)
mono_right = pipeline.create(dai.node.MonoCamera)

mono_left.setBoardSocket(dai.CameraBoardSocket.CAM_B)
mono_right.setBoardSocket(dai.CameraBoardSocket.CAM_C)
mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)

# === Stereo depth ===
stereo = pipeline.create(dai.node.StereoDepth)
stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_ACCURACY)
stereo.setLeftRightCheck(LR_CHECK)
stereo.setExtendedDisparity(EXTENDED_DISPARITY)
stereo.setSubpixel(SUBPIXEL)
stereo.setDepthAlign(dai.CameraBoardSocket.CAM_A)  # Align depth to RGB camera

# === Link cameras ===
mono_left.out.link(stereo.left)
mono_right.out.link(stereo.right)
color_cam.isp.link(stereo.colorCameraInput)

# === Outputs ===
xout_rgb = pipeline.create(dai.node.XLinkOut)
xout_depth = pipeline.create(dai.node.XLinkOut)
xout_rgb.setStreamName("rgb")
xout_depth.setStreamName("depth")

color_cam.video.link(xout_rgb.input)
stereo.depth.link(xout_depth.input)

# === Run pipeline ===
try:
    with dai.Device(pipeline) as device:
        rgb_q = device.getOutputQueue("rgb", maxSize=4, blocking=False)
        depth_q = device.getOutputQueue("depth", maxSize=4, blocking=False)

        calib = device.readCalibration()
        intrinsics = calib.getCameraIntrinsics(dai.CameraBoardSocket.CAM_A)
        focal_length_px = intrinsics[0][0]
        print("Focal length (pixels):", focal_length_px)

        max_disp = stereo.initialConfig.getMaxDisparity()

        cv2.namedWindow("RGB")
        cv2.namedWindow("Depth")

        while True:
            frame = rgb_q.get().getCvFrame()
            depth_map = depth_q.get().getFrame().astype(np.float32)

            h_frame, w_frame = frame.shape[:2]
            h_depth, w_depth = depth_map.shape[:2]

            # Ensure shape match
            if (h_frame, w_frame) != (h_depth, w_depth):
                depth_map = cv2.resize(depth_map, (w_frame, h_frame))

            # === YOLO detection on RGB ===
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
                    cv2.putText(frame, 'Cross', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.circle(frame, (c_x, c_y), 5, (0, 255, 0), -1)

            # === Depth estimation ===
            for ((x, y), w, h) in cross_info:
                x1 = max(0, min(w_frame - 1, int(x - w / 2)))
                y1 = max(0, min(h_frame - 1, int(y - h / 2)))
                x2 = max(0, min(w_frame - 1, int(x + w / 2)))
                y2 = max(0, min(h_frame - 1, int(y + h / 2)))

                roi = depth_map[y1:y2, x1:x2]
                valid_depths = roi[roi > 0]

                if valid_depths.size > 0:
                    depth_m = np.mean(valid_depths) / 1000.0
                    cv2.putText(frame, f'{depth_m:.2f}m', (x + 10, y + 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

            # Normalize depth for display
            norm_depth = (depth_map * (255.0 / max_disp)).astype(np.uint8)
            depth_vis = cv2.applyColorMap(norm_depth, cv2.COLORMAP_JET)

            # === Show frames ===
            cv2.imshow("RGB", frame)
            cv2.imshow("Depth", depth_vis)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)

finally:
    cv2.destroyAllWindows()
