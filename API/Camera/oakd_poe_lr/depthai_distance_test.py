#!/usr/bin/env python3

import cv2
import depthai as dai
import numpy as np
import math

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

# Connect to device and start pipeline
with dai.Device(pipeline) as device:
    #depth calculations made from right-most camera socket
    intrinsicData = device.readCalibration().getCameraIntrinsics(dai.CameraBoardSocket.CAM_C)
    # focal length measured in pixels can be found at the index below
    focal_length_in_pixels = intrinsicData[0][0]
    print("Cam C focal length in pixels: ", focal_length_in_pixels)
    #TODO: write depth calculation equation and output to stream
    #Oak-d has a 7.5cm baseline measurement, divide by the disparity value and get the distance measurement


    # Output queue will be used to get the disparity frames from the outputs defined above
    q = device.getOutputQueue(name="disparity", maxSize=4, blocking=False)

    while True:
        inDisparity = q.get()  # blocking call, will wait until a new data has arrived

        # get the disparity map and avoid 0 in the array
        disparity_map = inDisparity.getFrame().astype(np.float32)
        disparity_map[disparity_map==0] = 0.1

        # compute depth in meter
        depth_map = (focal_length_in_pixels*0.075)/disparity_map

        # check min and max depth
        print("Min depth:", np.min(depth_map))
        print("Max depth:", np.max(depth_map))


        # Normalize for better visualization
        depth_normalized = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)

        # Available color maps: https://docs.opencv.org/3.4/d3/d50/group__imgproc__colormap.html
        depth_colored = cv2.applyColorMap(depth_normalized.astype(np.uint8), cv2.COLORMAP_JET)

        # Create color legend (spectrum)
        spectrum_height = depth_colored.shape[0]
        spectrum_width = 50  # Adjust width as needed
        spectrum = np.linspace(0, 255, spectrum_height, dtype=np.uint8).reshape(spectrum_height, 1)
        spectrum = cv2.applyColorMap(spectrum, cv2.COLORMAP_JET)
        spectrum = cv2.resize(spectrum, (spectrum_width, spectrum_height))

        # Add distance labels
        num_labels = 5  # Adjust as needed
        for i in range(num_labels):
            y = int(spectrum_height - (i / (num_labels - 1)) * spectrum_height)
            distance = (i / (num_labels - 1)) * np.max(depth_map)  # Estimate depth values
            cv2.putText(spectrum, f"{int(distance)}cm", (5, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        
        #depth = (focal_length_in_pixels * 7.5) / 95 example depth calculation since I cannot find the disparity data anywhere
        # print(depth)
        #for grayscale output
        #cv2.imshow("disparity", frame)
        #output
        #cv2.putText(frame, f"Depth from sensor: {depth}cm", (10,10), cv2.FONT_HERSHEY_TRIPLEX, 0.4, (255,255,255))

        # Combine depth map and color spectrum
        combined = np.hstack((depth_colored, spectrum))
        
        cv2.imshow("Disparity", disparity_map.astype(np.uint8))
        #cv2.imshow("combined", combined)

        if cv2.waitKey(1) == ord('q'):
            break