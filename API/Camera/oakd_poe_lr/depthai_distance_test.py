#!/usr/bin/env python3

import cv2
import depthai as dai
import time

found, info = dai.DeviceBootloader.getFirstAvailableDevice()
"""
Starting off by debugging OAKD POE LR information and ensuring connection is established
so we can make a pipeline and then load it with \"nodes\". We will then configure the nodes
and load the pipeline onto the device. 
"""
# Connect to device and start pipeline
with dai.Device() as device:
    # Device static IPV4 output
    if found:
        print(f'Found device with IP Address: {info.name}')
    # Device name
    print('Device name:', device.getDeviceName())
    # Bootloader version
    if device.getBootloaderVersion() is not None:
        print('Bootloader version:', device.getBootloaderVersion())
    # Print out usb speed if connected to USB
    print('Usb speed:', device.getUsbSpeed().name)
    #print out cameras
    cams = device.getConnectedCameraFeatures()
    for cam in cams:
        print(str(cam), str(cam.socket), cam.socket)

    # Create pipeline, now we populate with nodes
    pipeline = dai.Pipeline()
    #TODO: define pipeline with attributes to calculate depth
    #TODO: use https://docs.luxonis.com/hardware/platform/depth/configuring-stereo-depth/#Configuring%20Stereo%20Depth-1.%20Stereo%20Depth%20Basics-How%20baseline%20distance%20and%20focal%20length%20affect%20depth for technical reference
    pipeline.create(None) #replace None w/ actual parameters


    # cams = device.getConnectedCameraFeatures()
    # streams = []
    # for cam in cams:
    #     print(str(cam), str(cam.socket), cam.socket)
    #     c = pipeline.create(dai.node.Camera)
    #     x = pipeline.create(dai.node.XLinkOut)
    #     c.isp.link(x.input)
    #     c.setBoardSocket(cam.socket)
    #     stream = str(cam.socket)
    #     if cam.name:
    #         stream = f'{cam.name} ({stream})'
    #     x.setStreamName(stream)
    #     streams.append(stream)

    # Start pipeline
    # device.startPipeline(pipeline)
    # fpsCounter = {}
    # lastFpsCount = {}
    # tfps = time.time()
    # while not device.isClosed():
    #     queueNames = device.getQueueEvents(streams)
    #     for stream in queueNames:
    #         messages = device.getOutputQueue(stream).tryGetAll()
    #         fpsCounter[stream] = fpsCounter.get(stream, 0.0) + len(messages)
    #         for message in messages:
    #             # Display arrived frames
    #             if type(message) == dai.ImgFrame:
    #                 # render fps
    #                 fps = lastFpsCount.get(stream, 0)
    #                 frame = message.getCvFrame()
    #                 cv2.putText(frame, "Fps: {:.2f}".format(fps), (10, 10), cv2.FONT_HERSHEY_TRIPLEX, 0.4, (255,255,255))
    #                 cv2.imshow(stream, frame)
    #
    #     if time.time() - tfps >= 1.0:
    #         scale = time.time() - tfps
    #         for stream in fpsCounter.keys():
    #             lastFpsCount[stream] = fpsCounter[stream] / scale
    #         fpsCounter = {}
    #         tfps = time.time()
    #
    #     if cv2.waitKey(1) == ord('q'):
    #         break
