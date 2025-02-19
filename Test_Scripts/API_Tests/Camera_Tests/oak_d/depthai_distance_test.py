#!/usr/bin/env python3

import cv2
import depthai as dai
import numpy as np
import sys

# Stereo depth settings
EXTENDED_DISPARITY = False  # Doubles disparity range
SUBPIXEL = True  # Improves accuracy
LR_CHECK = True  # Handles occlusions better

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

# Set stream name
xout_left.setStreamName("left")
xout_right.setStreamName("right")
xout.setStreamName("disparity")

# Configure left camera
left_cam.setBoardSocket(dai.CameraBoardSocket.CAM_B)
left_cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1200_P)
left_cam.setCamera("left")
left_cam.setIspScale(2, 3)

# Configure right camera
right_cam.setBoardSocket(dai.CameraBoardSocket.CAM_A)
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
stereo.disparity.link(xout.input)

# Link nodes for individual camera 
left_cam.isp.link(xout_left.input)
right_cam.isp.link(xout_right.input)

# Mouse callback function to display depth at hovered pixel
def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        depth_value = depth_map[y, x] if 0 <= y < depth_map.shape[0] and 0 <= x < depth_map.shape[1] else None
        disparity_value = disparity_map[y, x] if 0 <= y < disparity_map.shape[0] and 0 <= x < disparity_map.shape[1] else None
        if depth_value is not None:
            print(f"Disparity at ({x}, {y}): {disparity_value:.2f} pixels | Depth: {depth_value:.2f} cm", end="\r")


try:
    with dai.Device(pipeline) as device:
        # Retrieve camera calibration data
        intrinsic_dataB = device.readCalibration().getCameraIntrinsics(dai.CameraBoardSocket.CAM_B)
        intrinsic_dataC = device.readCalibration().getCameraIntrinsics(dai.CameraBoardSocket.CAM_C)
        focal_lengthB = intrinsic_dataB[0][0]
        focal_lengthC = intrinsic_dataC[0][0]

        print("Cam B focal length in pixels:", focal_lengthC)
        print("Cam C focal length in pixels:", focal_lengthC)
        left_q = device.getOutputQueue(name="left", maxSize=4, blocking=False)
        right_q = device.getOutputQueue(name="right", maxSize=4, blocking=False)
        q = device.getOutputQueue(name="disparity", maxSize=4, blocking=False)

        cv2.namedWindow("Depth Map")
        cv2.setMouseCallback("Depth Map", on_mouse)

        while True:
            try:
                # display original image of two cameras
                cv2.imshow("Left Camera", left_q.get().getCvFrame())
                cv2.imshow("Right Camera", right_q.get().getCvFrame())

                # Get disparity frame
                in_disparity = q.get()
                disparity_map = in_disparity.getCvFrame()

                cv2.imshow("raw disparity", in_disparity.getCvFrame())
                
                # Compute depth map
                depth_map = (focal_lengthC * 15) / np.maximum(disparity_map, 0.001) # divide by 32 because subpixel is on, scale back down
                depth_map = np.clip(depth_map, 0, 3000)  # Limit depth to 30m

                # Normalize disparity for visualization
                max_disparity = stereo.initialConfig.getMaxDisparity()
                depth_normalized = (disparity_map * (255 / max_disparity)).astype(np.uint8)
                depth_colored = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)
                
                cv2.imshow("Depth Map", depth_colored)
                
                if cv2.waitKey(1) == ord('q'):
                    break
            except Exception as e:
                print(f"Error processing frame: {e}")
                break

except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)

finally:
    cv2.destroyAllWindows()
