import json
import time
import random

import cv2
import numpy as np

import depthai as dai

from typing import Tuple
from datetime import timedelta


class CameraInterface:
    def __init__(
        self
    ):
        self.framesToAccumulation = 5
        self.FPS                  = 30

        self.streamNameColor     = "color"
        self.streamNameLeft      = "left"
        self.streamNameRight     = "right"
        self.streamNameColorIn   = "colorIn"
        self.streamNameLeftIn    = "leftIn"
        self.streamNameRightIn   = "rightIn"
        self.streamNameDisparity = "disparity"
        self.streamNameDepth     = "depth"
        self.streamNameScript    = "script"
        self.streamStatus        = "status"

        self.nameAccumulationScript = "Stream Accumulation Valve"
        self.namePassScript         = "Stream Pass Valve"

        self.COLOR_CAMERA_SOCKET = dai.CameraBoardSocket.RGB
        self.LEFT_CAMERA_SOCKET  = dai.CameraBoardSocket.LEFT
        self.RIGHT_CAMERA_SOCKET = dai.CameraBoardSocket.RIGHT

        # In miliseconds
        self.syncThreshold = 1000 / self.FPS

        self.device = dai.Device()

        self.device.setTimesync(timedelta(seconds=5), 10, True)

        self.device.setLogLevel(dai.LogLevel.DEBUG)
        self.device.setLogOutputLevel(dai.LogLevel.DEBUG)

        self.calibration = self.device.readCalibration()

        self.COLOR_RESOLUTION = dai.ColorCameraProperties.SensorResolution.THE_4_K
        self.MONO_RESOLUTION  = dai.MonoCameraProperties.SensorResolution.THE_480_P

        # 4K
        self.imageWidth  = 3840
        self.imageHeight = 2160


    def startCapture(self):
        self._initPipeline()

        self._setProperties()

        self._linkPipeline()

        self.device.startPipeline(self.pipeline)

        self._initQueues()


    def stopCapture(self):
        if self.device:
            self.device.close()

        self.device   = None
        self.pipeline = None


    def triggerFramePass(self):
        if self.scriptQueue:
            print(f"Trigger at: {dai.Clock.now().total_seconds()}")

            buf = dai.Buffer()
            buf.setData(True)

            self.scriptQueue.send(buf)
        else:
            print("Pipeline not inited")


    def getBuffers(self):
        colorBuffer     = None
        depthBuffer     = None

        EOS = False

        while True:
            statusData = self.statusQueue.tryGet()

            if statusData:
                statusText = str(statusData.getData(), 'utf-8')
                data = json.loads(statusText)

                if data["status"] == "invalid":
                    EOS = True
                    break

                if data["status"] == "valid":
                    colorBuffer = self.colorQueue.get()
                    depthBuffer = self.depthQueue.get()
                    break

        return (
            EOS,
            colorBuffer,
            depthBuffer
        )


    def _initPipeline(self):
        self.pipeline = dai.Pipeline()

        # Improves latency: https://discuss.luxonis.com/d/731-how-to-increase-oakd-lite-s-stereo-pair-frame-rate
        self.pipeline.setXLinkChunkSize(0)

        self.pipeline.setCalibrationData(self.calibration)

        self.color     = self.pipeline.create(dai.node.ColorCamera)
        self.xoutColor = self.pipeline.createXLinkOut()
        self.xoutColor.setStreamName(self.streamNameColor)



        self.monoLeft  = self.pipeline.create(dai.node.MonoCamera)
        self.monoRight = self.pipeline.create(dai.node.MonoCamera)


        self.stereoDepth = self.pipeline.create(dai.node.StereoDepth)
        self.xoutDepth   = self.pipeline.create(dai.node.XLinkOut)
        self.xoutDepth.setStreamName(self.streamNameDepth)


        self.accumulationScript = self.pipeline.create(dai.node.Script)
        self.passScript         = self.pipeline.create(dai.node.Script)

        self.xinScript = self.pipeline.create(dai.node.XLinkIn)
        self.xinScript.setStreamName(self.streamNameScript)


        self.xoutStatus = self.pipeline.create(dai.node.XLinkOut)
        self.xoutStatus.setStreamName(self.streamStatus)


        self.sync  = self.pipeline.create(dai.node.Sync)
        self.demux = self.pipeline.create(dai.node.MessageDemux)


        mesh, meshWidth, meshHeight = self._getMesh(
            self.calibration,
            self.COLOR_CAMERA_SOCKET,
            (self.imageWidth, self.imageHeight)
        )

        self.manip = self.pipeline.create(dai.node.ImageManip)
        self.manip.setWarpMesh(mesh, meshWidth, meshHeight)
        self.manip.setMaxOutputFrameSize(self.imageWidth * self.imageHeight * 3)


    def _setProperties(self):
        self.color.setBoardSocket(self.COLOR_CAMERA_SOCKET)
        self.color.setResolution(self.COLOR_RESOLUTION)
        self.color.setFps(self.FPS)


        self.monoLeft.setBoardSocket(self.LEFT_CAMERA_SOCKET)
        self.monoLeft.setFps(self.FPS)
        self.monoLeft.setResolution(self.MONO_RESOLUTION)

        self.monoRight.setBoardSocket(self.RIGHT_CAMERA_SOCKET)
        self.monoRight.setFps(self.FPS)
        self.monoRight.setResolution(self.MONO_RESOLUTION)


        self.stereoDepth.setDepthAlign(self.COLOR_CAMERA_SOCKET)
        self.stereoDepth.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_ACCURACY)
        self.stereoDepth.setLeftRightCheck(True)


        accumulationScript = f"""
        passed = 0

        while True:
            # Drop all color/left/right frames except the last one
            colorFrame = node.io['inColor'].get()
            leftFrame  = node.io['inLeft'].get()
            rightFrame = node.io['inRight'].get()

            trigger = node.io['inTrigger'].tryGet()

            if trigger:
                passed = {self.framesToAccumulation}

            if passed > 0:
                node.warn("Accumulation: " + str(passed))
                passed -= 1

                # Send only the last color frame
                if passed == 0:
                    node.io['outColor'].send(colorFrame)

                    monoSN = leftFrame.getSequenceNum()
                    colorFrame.setSequenceNum(monoSN)

                node.io['outLeft'].send(leftFrame)
                node.io['outRight'].send(rightFrame)

                node.warn("Mono SN: " + str(leftFrame.getSequenceNum()))
        """

        self.accumulationScript.setScript(
            script = accumulationScript,
            name   = self.nameAccumulationScript
        )

        passScript = f"""
            import time
            import json

            colorFrame = None
            depthFrame = None

            startTime   = None
            timeoutTime = 0.200 # in seconds
            timeoutPass = False

            statusBuffer = Buffer(30)

            while True:
                # Try to get color frame
                currentColorFrame = node.io['inColor'].tryGet()

                if currentColorFrame:
                    colorFrame = currentColorFrame
                    startTime = Clock.now().total_seconds()

                    colorSN = colorFrame.getSequenceNum()
                    node.warn("color: " + str(colorSN))

                if colorFrame:
                    currentTime = Clock.now().total_seconds()
                    delta = currentTime - startTime

                    if delta >= timeoutTime:
                        if depthFrame:
                            status = {{"status": "valid"}}
                            statusBuffer.setData(json.dumps(status).encode('utf-8'))

                            node.io['outColor'].send(colorFrame)
                            node.io['outDepth'].send(depthFrame)
                            node.io['outStatus'].send(statusBuffer)

                            colorFrame = None
                            depthFrame = None
                            timeoutPass = False

                            node.warn("Delta: " + str(delta))
                            node.warn("Pass (Timeout)")

                        elif timeoutPass:
                            status = {{"status": "invalid"}}
                            statusBuffer.setData(json.dumps(status).encode('utf-8'))

                            node.io['outStatus'].send(statusBuffer)

                            colorFrame = None
                            depthFrame = None
                            timeoutPass = False

                            node.warn("Delta: " + str(delta))
                            node.warn("Timeout Hard Pass")

                        else:
                            timeoutPass = True
                            node.warn("Timeout Pass ON")

                # Drop all depth frames except the matching one
                currentDepthFrame = node.io['inDepth'].tryGet()

                if currentDepthFrame:
                    depthFrame = currentDepthFrame

                    depthSN = depthFrame.getSequenceNum()
                    node.warn("depth: " + str(depthSN))

                if colorFrame and depthFrame:
                    colorSN = colorFrame.getSequenceNum()
                    depthSN = depthFrame.getSequenceNum()

                    if colorSN == depthSN or timeoutPass:
                        status = {{"status": "valid"}}
                        statusBuffer.setData(json.dumps(status).encode('utf-8'))

                        node.io['outColor'].send(colorFrame)
                        node.io['outDepth'].send(depthFrame)

                        node.io['outStatus'].send(statusBuffer)

                        colorFrame = None
                        depthFrame = None
                        timeoutPass = False

                        node.warn(f"Pass")
                time.sleep(0.005)
        """

        self.passScript.setScript(
            script = passScript,
            name   = self.namePassScript
        )

        self.sync.setSyncThreshold(timedelta(milliseconds=self.syncThreshold))
        self.sync.setSyncAttempts(-1)


    def _linkPipeline(self):
        # Link from Color/Mono components to Sync inputs
        self.color.isp.link(self.sync.inputs["colorSync"])
        self.monoLeft.out.link(self.sync.inputs["leftSync"])
        self.monoRight.out.link(self.sync.inputs["rightSync"])

        # Link Sync output to Demux input
        self.sync.out.link(self.demux.input)

        # # Link Demux outputs to Accumulation Script inputs
        self.demux.outputs["colorSync"].link(self.accumulationScript.inputs["inColor"])
        self.demux.outputs["leftSync"].link(self.accumulationScript.inputs["inLeft"])
        self.demux.outputs["rightSync"].link(self.accumulationScript.inputs["inRight"])

        # Link Accumulation Script trigger input
        self.xinScript.out.link(self.accumulationScript.inputs['inTrigger'])

        # Link Accumulation Script outputs based on configuration
        self.accumulationScript.outputs["outColor"].link(self.manip.inputImage)
        self.accumulationScript.outputs["outLeft"].link(self.stereoDepth.left)
        self.accumulationScript.outputs["outRight"].link(self.stereoDepth.right)

        # Link StereoDepth output to Pass Script input
        self.stereoDepth.depth.link(self.passScript.inputs["inDepth"])

        # Link Undistortion output to Pass Script input if in use
        self.manip.out.link(self.passScript.inputs["inColor"])

        # Link Pass Script outputs based on configuration
        self.passScript.outputs["outColor"].link(self.xoutColor.input)
        self.passScript.outputs["outDepth"].link(self.xoutDepth.input)

        self.passScript.outputs["outStatus"].link(self.xoutStatus.input)


    def _initQueues(self):
        outputFrames = 1

        self.colorQueue = self.device.getOutputQueue(name=self.streamNameColor, maxSize=outputFrames, blocking=True)
        self.depthQueue = self.device.getOutputQueue(name=self.streamNameDepth, maxSize=outputFrames, blocking=False)

        self.scriptQueue = self.device.getInputQueue(name=self.streamNameScript, maxSize=outputFrames, blocking=True)
        self.statusQueue = self.device.getOutputQueue(name=self.streamStatus,    maxSize=outputFrames, blocking=False)


    def _getMesh(
        self,
        calibrationData : dai.CalibrationHandler,
        cameraSocket : dai.CameraBoardSocket,
        ispSize : Tuple[int, int]
    ):
        M1 = np.array(calibrationData.getCameraIntrinsics(cameraSocket, ispSize[0], ispSize[1]))
        d1 = np.array(calibrationData.getDistortionCoefficients(cameraSocket))
        R1 = np.identity(3)

        mapX, mapY = cv2.initUndistortRectifyMap(M1, d1, R1, M1, ispSize, cv2.CV_32FC1)

        meshCellSize = 16
        mesh0 = []
        # Creates subsampled mesh which will be loaded on to device to undistort the image
        for y in range(mapX.shape[0] + 1): # iterating over height of the image
            if y % meshCellSize == 0:
                rowLeft = []
                for x in range(mapX.shape[1]): # iterating over width of the image
                    if x % meshCellSize == 0:
                        if y == mapX.shape[0] and x == mapX.shape[1]:
                            rowLeft.append(mapX[y - 1, x - 1])
                            rowLeft.append(mapY[y - 1, x - 1])
                        elif y == mapX.shape[0]:
                            rowLeft.append(mapX[y - 1, x])
                            rowLeft.append(mapY[y - 1, x])
                        elif x == mapX.shape[1]:
                            rowLeft.append(mapX[y, x - 1])
                            rowLeft.append(mapY[y, x - 1])
                        else:
                            rowLeft.append(mapX[y, x])
                            rowLeft.append(mapY[y, x])
                if (mapX.shape[1] % meshCellSize) % 2 != 0:
                    rowLeft.append(0)
                    rowLeft.append(0)

                mesh0.append(rowLeft)

        mesh0 = np.array(mesh0)
        meshWidth = mesh0.shape[1] // 2
        meshHeight = mesh0.shape[0]
        mesh0.resize(meshWidth * meshHeight, 2)

        mesh = list(map(tuple, mesh0))

        return mesh, meshWidth, meshHeight

if __name__ == "__main__":
    camera = CameraInterface()

    windowSize = (1280, 980)

    cv2.namedWindow("color", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("color", windowSize)

    cv2.namedWindow("depth", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("depth", windowSize)

    exitNow = False

    for idxOut in range(37):
        camera.startCapture()

        delay = 0.000

        if idxOut % 5 == 0:
            delay = random.uniform(0.0, 3.0)

        for idxIn in range(1337):
            print(f"============== Run: {idxOut}:{idxIn} | Delay: {delay:.3} ==============")
            time.sleep(delay)

            camera.triggerFramePass()
            EOS, colorBuffer, depthBuffer = camera.getBuffers()

            if EOS:
                print("Hard Timeout EOS!")
                break

            colorFrame = colorBuffer.getCvFrame()
            depthFrame = depthBuffer.getCvFrame()

            depthFrame = (depthFrame / 10).astype(np.uint8)

            cv2.waitKey(1)
            cv2.imshow("color", colorFrame)
            cv2.imshow("depth", depthFrame)

        camera.stopCapture()