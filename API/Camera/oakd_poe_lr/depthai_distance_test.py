#!/usr/bin/env python3

import cv2
import depthai as dai
import numpy as np
import math

# Closer-in minimum depth, disparity range is doubled (from 95 to 190):
extended_disparity = False
# Better accuracy for longer distance, fractional disparity 32-levels:
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
    #focal length measured in pixels can be found at the index below
    focal_length_in_pixels = device.readCalibration().getCameraIntrinsics(dai.CameraBoardSocket.CAM_C)
    print("Cam C focal length in pixels: ", focal_length_in_pixels[0][0])
    #TODO: write depth calculation equation and output to stream
    # depth = device.readCalibration().getCamera
    #

    # Output queue will be used to get the disparity frames from the outputs defined above
    q = device.getOutputQueue(name="disparity", maxSize=4, blocking=False)

    while True:
        inDisparity = q.get()  # blocking call, will wait until a new data has arrived
        frame = inDisparity.getFrame()
        # Normalization for better visualization
        frame = (frame * (255 / stereo.initialConfig.getMaxDisparity())).astype(np.uint8)

        #for grayscale output
        #cv2.imshow("disparity", frame)

        # Available color maps: https://docs.opencv.org/3.4/d3/d50/group__imgproc__colormap.html
        frame = cv2.applyColorMap(frame, cv2.COLORMAP_JET)
        cv2.imshow("disparity_color", frame)

        if cv2.waitKey(1) == ord('q'):
            break