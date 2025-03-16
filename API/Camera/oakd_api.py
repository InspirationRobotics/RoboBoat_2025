import cv2
import numpy as np
import depthai as dai
import threading
import queue
import time

class OAKD_LR:
    def __init__(self, model_path: str, labelMap: list ,debug:bool = False):
        self.FPS = 5
        self.extended_disparity = True
        self.subpixel = True
        self.lr_check = True

        # config for NN detection
        self.syncNN = True
        self.nnPath = model_path
        self.labelMap = labelMap
        self.confidenceThreshold = 0.5

        if(self._findCamera()):
            self.device = dai.Device()
        else:
            print("ERROR: DID NOT FOUND OAK_D CAMERA")
            self.device = None
        self.COLOR_RESOLUTION = dai.ColorCameraProperties.SensorResolution.THE_1200_P
        self.imageWidth = 1920
        self.imageHeight = 1200

        self.debug = debug
    def _initPipeline(self):
        self.pipeline = dai.Pipeline()
        # 3 cameras
        self.leftCam = self.pipeline.create(dai.node.ColorCamera)
        self.rightCam = self.pipeline.create(dai.node.ColorCamera)
        self.centerCam = self.pipeline.create(dai.node.ColorCamera)

        # depth map
        self.stereo = self.pipeline.create(dai.node.StereoDepth)

        # Neural network
        self.detection = self.pipeline.create(dai.node.YoloDetectionNetwork)
        self.manip = self.pipeline.create(dai.node.ImageManip)

        # Output nodes
        self.xoutRgb = self.pipeline.create(dai.node.XLinkOut)
        self.xoutDepth = self.pipeline.create(dai.node.XLinkOut)
        self.xoutYolo = self.pipeline.create(dai.node.XLinkOut)

        # set stream name
        self.xoutRgb.setStreamName("rgb")
        self.xoutDepth.setStreamName("depth")
        self.xoutYolo.setStreamName("yolo")


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

        self.detection.setConfidenceThreshold(self.confidenceThreshold)
        self.detection.setNumClasses(len(self.labelMap))
        self.detection.setCoordinateSize(4)
        self.detection.setIouThreshold(0.5)
        self.detection.setBlobPath(self.nnPath)
        self.detection.setNumInferenceThreads(2)
        self.detection.input.setBlocking(False)

        self.manip.initialConfig.setResize(640, 352)
        self.manip.initialConfig.setCropRect(0, 0, 640, 352)
        self.manip.setFrameType(dai.ImgFrame.Type.BGR888p)

    def _linkStereo(self):
        self.leftCam.isp.link(self.stereo.left)
        self.rightCam.isp.link(self.stereo.right)
        self.stereo.depth.link(self.xoutDepth.input)

    def _linkNN(self):
        self.centerCam.preview.link(self.manip.inputImage)
        self.manip.out.link(self.detection.input)
        
        if self.syncNN:
            self.detection.passthrough.link(self.xoutRgb.input)
        else:
            self.centerCam.preview.link(self.xoutRgb.input)

        self.detection.out.link(self.xoutYolo.input)        

    def _initQueues(self):
        self.qRgb = self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        self.qDepth = self.device.getOutputQueue(name="depth", maxSize=4, blocking=False)
        self.qDet = self.device.getOutputQueue(name="yolo", maxSize=4, blocking=False)

        if self.debug:
            print(f"[DEBUG] qRGB type: {type(self.qRgb)} -> {self.qRgb}")
            print(f"[DEBUG] qDepth type: {type(self.qDepth)} -> {self.qDepth}")


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
            print("[DEBUG] Device running.")

        print("[DEBUG] Starting pipeline...")
        self._initPipeline()
        self._setProperties()
        self._linkNN()
        self._linkStereo()
        self.device.startPipeline(self.pipeline)

        print("[DEBUG] Pipeline initialized.")

        self._initQueues()

    def stopCapture(self):
        if self.device:
            self.device.close()

    def getLatestBuffers(self):
        res = self.qRgb.get().getCvFrame()
        return res
    
    def getLatestDepth(self):
        res = self.qDepth.get().getCvFrame()
        return res
    
    def getLatestDetection(self):
        res = self.qDet.get().detections
        return res

if __name__ == "__main__":
    from GNC.Guidance_Core.mission_helper import MissionHelper
    # Load config
    config = MissionHelper().load_json(path="GNC/Guidance_Core/Config/barco_polo.json")

    # Define paths to models
    MODEL_1 = config["test_model_path"]
    MODEL_2 = config["competition_model_path"]

    # Label Map (Ensure it matches your detection classes)
    LABELMAP_1 = config["test_label_map"]
    LABELMAP_2 = config["competition_label_map"]

    cam = OAKD_LR(model_path=MODEL_2,labelMap=LABELMAP_2)
    cam.startCapture()

    while(True):  # count for 100s to display frames
        buffer = cam.getLatestBuffers()

        cv2.imshow("frame", buffer)

        if cv2.waitKey(100) & 0xFF == ord('q'):  # Exit on pressing 'q'
            break

    cv2.destroyAllWindows()