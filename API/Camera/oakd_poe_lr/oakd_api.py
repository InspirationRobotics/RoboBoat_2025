import cv2
import numpy as np
import depthai as dai
import threading
import queue
import time

class OAKD_LR:
    def __init__(self):
        self.FPS = 20
        self.extended_disparity = True
        self.subpixel = True
        self.lr_check = True

        if(self._findCamera()):
            self.device = dai.Device()
        else:
            print("ERROR: DID NOT FOUND OAK_D CAMERA")
            self.device = None
        self.COLOR_RESOLUTION = dai.ColorCameraProperties.SensorResolution.THE_1200_P
        self.imageWidth = 1920
        self.imageHeight = 1200

        # Threading components
        self.running = False
        self.frame_queue = queue.Queue(maxsize=4)
        self.det_queue = queue.Queue(maxsize=4)
        self.lock = threading.Lock()

        self.capture_thread = None

    def _initPipeline(self):
        self.pipeline = dai.Pipeline()
        # 3 cameras
        self.leftCam = self.pipeline.create(dai.node.ColorCamera)
        self.rightCam = self.pipeline.create(dai.node.ColorCamera)
        self.centerCam = self.pipeline.create(dai.node.ColorCamera)

        # depth map
        self.stereo = self.pipeline.create(dai.node.StereoDepth)

        # Out put node
        self.xoutRgb = self.pipeline.create(dai.node.XLinkOut)
        self.xoutDepth = self.pipeline.create(dai.node.XLinkOut)


        # set stream name
        self.xoutRgb.setStreamName("rgb")
        self.xoutDepth.setStreamName("depth")


    def _setProperties(self):
        self.leftCam.setIspScale(2, 3)
        self.leftCam.setCamera("left")
        self.leftCam.setResolution(self.COLOR_RESOLUTION)
        self.leftCam.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
        self.leftCam.setFps(self.FPS)

        self.rightCam.setIspScale(2, 3)
        self.rightCam.setCamera("right")
        self.rightCam.setResolution(self.COLOR_RESOLUTION)
        self.rightCam.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
        self.rightCam.setFps(self.FPS)

        self.centerCam.setIspScale(2, 3)
        self.centerCam.setCamera("center")
        self.centerCam.setResolution(self.COLOR_RESOLUTION)
        self.centerCam.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
        self.centerCam.setFps(self.FPS)

        #self.stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.DEFAULT) # this make the window smaller for some reason
        self.stereo.initialConfig.setMedianFilter(dai.MedianFilter.MEDIAN_OFF)
        self.stereo.setLeftRightCheck(self.lr_check)
        self.stereo.setExtendedDisparity(self.extended_disparity)
        self.stereo.setSubpixel(self.subpixel)

    def _linkStereo(self):
        self.leftCam.isp.link(self.stereo.left)
        self.rightCam.isp.link(self.stereo.right)
        self.stereo.depth.link(self.xoutDepth.input)

    def _linkRGB(self):
        self.centerCam.isp.link(self.xoutRgb.input)           

    def _initQueues(self):
        self.qRgb = self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        self.qDepth = self.device.getOutputQueue(name="depth", maxSize=4, blocking=False)

    def _findCamera(self) -> bool:
        """ Check if a DepthAI device exists """
        try:
            # Get available devices
            available_devices = dai.Device.getAllConnectedDevices()

            # Check if any device is found
            if len(available_devices) == 0:
                print("[ERROR] No DepthAI devices found.")
                return False
            
            # If a device is found, print the device info and return True
            print(f"Found DepthAI device: {available_devices[0].getMxId()}")
            return True

        except RuntimeError as e:
            # Handle exceptions (e.g., if the device cannot be found)
            print(f"[ERROR] Failed to find DepthAI camera: {e}")
            return False

    def startCapture(self):
        if not self.device:
            print("[ERROR] Device is not running!")
            return
        else:
            print("Device running.")

        print("Starting pipeline...")
        self._initPipeline()
        self._setProperties()
        self._linkRGB()
        self._linkStereo()
        self.device.startPipeline(self.pipeline)
        print("Pipeline initialized.")
        self._initQueues()

        time.sleep(1)  # wait for frame to arrive queue
        res = self.getLatestBuffers()
        cv2.imshow("buffer", res)
    def stopCapture(self):
        if self.device:
            self.device.close()

    def getLatestBuffers(self):
        res = self.qRgb.get().getCvFrame()
        return res

"""some function for processing"""

if __name__ == "__main__":
    cam = OAKD_LR()
    cam.startCapture()

    counter = 0
    while(counter < 100):
        buffer = cam.getLatestBuffers()
        cv2.imshow("frame", buffer)
        print(counter)
        counter +=1
        time.sleep(1)


    cv2.destroyAllWindows()

