import cv2
import depthai as dai
import numpy as np

# Create a DepthAI pipeline
pipeline = dai.Pipeline()

# Create nodes for left, right, and color cameras
left_cam = pipeline.create(dai.node.MonoCamera)
right_cam = pipeline.create(dai.node.MonoCamera)
color_cam = pipeline.create(dai.node.ColorCamera)

# Create output nodes
xout_left = pipeline.create(dai.node.XLinkOut)
xout_right = pipeline.create(dai.node.XLinkOut)
xout_color = pipeline.create(dai.node.XLinkOut)

# Set stream names
xout_left.setStreamName("left")
xout_right.setStreamName("right")
xout_color.setStreamName("color")

# Configure left and right cameras (monochrome)
left_cam.setBoardSocket(dai.CameraBoardSocket.LEFT)
right_cam.setBoardSocket(dai.CameraBoardSocket.RIGHT)
left_cam.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
right_cam.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)

# Configure color camera
color_cam.setBoardSocket(dai.CameraBoardSocket.RGB)
color_cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
color_cam.setIspScale(2, 3)  # Reduce resolution if needed

# Linking cameras to outputs
left_cam.out.link(xout_left.input)
right_cam.out.link(xout_right.input)
color_cam.isp.link(xout_color.input)

# Connect to the device and start the pipeline
with dai.Device(pipeline) as device:
    left_q = device.getOutputQueue(name="left", maxSize=4, blocking=False)
    right_q = device.getOutputQueue(name="right", maxSize=4, blocking=False)
    color_q = device.getOutputQueue(name="color", maxSize=4, blocking=False)

    print("Capturing images...")

    # Get frames
    left_frame = left_q.get().getCvFrame()
    right_frame = right_q.get().getCvFrame()
    color_frame = color_q.get().getCvFrame()

    # Save images
    cv2.imwrite("left_camera.jpg", left_frame)
    cv2.imwrite("right_camera.jpg", right_frame)
    cv2.imwrite("color_camera.jpg", color_frame)

    print("Images saved successfully!")

    # Display images (optional)
    cv2.imshow("Left Camera", left_frame)
    cv2.imshow("Right Camera", right_frame)
    cv2.imshow("Color Camera", color_frame)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
