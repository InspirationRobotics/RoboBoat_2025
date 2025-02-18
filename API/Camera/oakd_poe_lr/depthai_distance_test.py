#!/usr/bin/env python3

import cv2
import depthai as dai
import numpy as np
import math
import sys

# Closer-in minimum depth, disparity range is doubled (from 95 to 190) when set to true:
extended_disparity = False
# Better accuracy for longer distance when set to true, fractional disparity 32-levels:
subpixel = True
# Better handling for occlusions:
lr_check = True

# Create pipeline
pipeline = dai.Pipeline()

# creating left and right colorcamera nodes, which will be linked and fed as input to our stereodepth node
colorLeft = pipeline.create(dai.node.ColorCamera)
colorRight = pipeline.create(dai.node.ColorCamera)
stereo = pipeline.create(dai.node.StereoDepth)
xout = pipeline.create(dai.node.XLinkOut)

xout.setStreamName("disparity")

# Properties
colorLeft.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1200_P)
colorLeft.setCamera("left") #refers to cam b
#setIspScale can take a numerator and denominator as input, so here we are setting output to 2/3rds the original size
colorLeft.setIspScale(2, 3)
colorRight.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1200_P)
colorRight.setCamera("right") #refers to cam c
colorRight.setIspScale(2,3)

# Create a node that will produce the depth map (using disparity output as it's easier to visualize depth this way)
stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.DEFAULT)
# Options: MEDIAN_OFF, KERNEL_3x3, KERNEL_5x5, KERNEL_7x7 (default)
stereo.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
stereo.setLeftRightCheck(lr_check)
stereo.setExtendedDisparity(extended_disparity)
stereo.setSubpixel(subpixel)

# Linking, using ISP engine. Must use isp.link for colorcamera nodes. for monocamera we can use *.out.link(nodename)
colorLeft.isp.link(stereo.left)
colorRight.isp.link(stereo.right)
stereo.disparity.link(xout.input)


# Try to connect to device and handle errors gracefully
try:
    with dai.Device(pipeline) as device:
        # Device is connected, retrieve calibration data
        intrinsicData = device.readCalibration().getCameraIntrinsics(dai.CameraBoardSocket.CAM_C)
        focal_length_in_pixels = intrinsicData[0][0]
        print("Cam C focal length in pixels: ", focal_length_in_pixels)

        q = device.getOutputQueue(name="disparity", maxSize=4, blocking=False)

        while True:
            try:
                # Get disparity frame
                inDisparity = q.get()

                # Get the disparity map and avoid 0 in the array
                disparity_map = inDisparity.getFrame()
                print(f"max disparity: {stereo.initialConfig.getMaxDisparity()}")
                disparity_map[disparity_map == 0] = 0.1

                # Normalize disparity map
                disparity_map = (disparity_map * (255 / stereo.initialConfig.getMaxDisparity())).astype(np.uint8)
                # Available color maps: https://docs.opencv.org/3.4/d3/d50/group__imgproc__colormap.html
                disparity_map = cv2.applyColorMap(disparity_map, cv2.COLORMAP_JET)
                cv2.imshow("Disparity", disparity_map)

                # Compute depth in cm
                depth_map = (focal_length_in_pixels * 7.5) / disparity_map
                print("Min depth:", np.min(depth_map))
                print("Max depth:", np.max(depth_map))

                depth_normalized = (disparity_map * (255 / stereo.initialConfig.getMaxDisparity())).astype(np.uint8)
                depth_colored = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)

                # Create color spectrum
                spectrum_height = depth_colored.shape[0]
                spectrum_width = 50
                spectrum = np.linspace(0, 255, spectrum_height, dtype=np.uint8).reshape(spectrum_height, 1)
                spectrum = cv2.applyColorMap(spectrum, cv2.COLORMAP_JET)
                spectrum = cv2.resize(spectrum, (spectrum_width, spectrum_height))

                # Add labels
                num_labels = 5
                for i in range(num_labels):
                    y = int(spectrum_height - (i / (num_labels - 1)) * spectrum_height)
                    distance = (i / (num_labels - 1)) * np.max(depth_map)
                    cv2.putText(spectrum, f"{int(distance)}cm", (0, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                combined = np.hstack((depth_colored, spectrum))
                # cv2.imshow("Combined", combined)

                if cv2.waitKey(1) == ord('q'):
                    break

            except Exception as e:
                print(f"Error in processing frame: {e}")
                break  # Exit loop on error

except dai.DeviceException as e:
    print(f"Error with device: {e}")
    sys.exit(1)  # Exit gracefully when device-related error occurs

except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)  # Exit gracefully on unexpected error

finally:
    cv2.destroyAllWindows()  # Make sure OpenCV windows are closed after execution