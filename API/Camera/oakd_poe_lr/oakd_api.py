"""
WORK IN PROGRESS
This is the api for setting up pipleine for oakd LR camera and get neural network detection and depth map
Example api format: https://discuss.luxonis.com/d/4702-capture-color-and-depth-only-on-event/8 
"""
import cv2
import numpy as np
import depthai as dai


# TODO add more comment
# TODO add find camera function to check camera existence
# TODO add threading
# TODO figure out threading, the program is unacceptably slow

class OAKD_LR:
    def __init__(self, model_path:str, labelMap:list):
        # set up pipeline
        self.FPS = 30
        
        # Stereo process options
        # Closer-in minimum depth, disparity range is doubled (from 95 to 190):
        self.extended_disparity = True
        # Better accuracy for longer distance, fractional disparity 32-levels:
        self.subpixel           = True
        # Better handling for occlusions:
        self.lr_check           = True

        # Yolo nn network information
        self.syncNN             = True
        # if true, the frame is sent after detection,
        # if false, frames come direftly from the left camera preview bypassing the neural network
        self.nnPath             = model_path
        self.labelMap           = labelMap   # need to be filled with out own label map
        self.confidenceThreshold= 0.5

        # Creating camera nodes
        self.streamNameLeft     = "left"
        self.streamNameRight    = "right"
        self.streamNameCenter   = "center"
        self.streamNameDisparity= "disparity"
        self.streamNameDepth    = "depth"

        self.device             = dai.Device()

        self.COLOR_RESOLUTION   = dai.ColorCameraProperties.SensorResolution.THE_1200_P

        self.imageWidth         = 1920
        self.imageHeight        = 1200
        pass
    

    def _initPipleline(self):
        # Initialize pipeline
        self.pipeline   = dai.Pipeline()

        # Create camera nodes
        self.leftCam    = self.pipeline.create(dai.node.ColorCamera)
        self.rightCam   = self.pipeline.create(dai.node.ColorCamera)
        self.centerCam  = self.pipeline.create(dai.node.ColorCamera)
        # Create stereo node for depth calculation
        self.stereo     = self.pipeline.create(dai.node.StereoDepth)          
        # Creat Yolo network node
        self.detection  = self.pipeline.create(dai.node.YoloDetectionNetwork)
        
        # Convertion node to convert image to correct format
        self.manip = self.pipeline.create(dai.node.ImageManip)

        # Define Xlink output nodes
        self.xoutRgb    = self.pipeline.create(dai.node.XLinkOut)
        self.xoutDepth  = self.pipeline.create(dai.node.XLinkOut)
        self.xoutYolo   = self.pipeline.create(dai.node.XLinkOut)

        # Set ouput stream name
        self.xoutRgb.setStreamName("rgb")
        self.xoutDepth.setStreamName("depth")
        self.xoutYolo.setStreamName("yolo")


    def _setProperties(self):
        # Left camera properties
        self.leftCam.setIspScale(2, 3)
        self.leftCam.setPreviewSize(640, 352)
        self.leftCam.setCamera("left")
        self.leftCam.setResolution(self.COLOR_RESOLUTION)
        self.leftCam.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
        self.leftCam.setFps(self.FPS)

        # Right camera properties
        self.rightCam.setIspScale(2, 3)
        self.rightCam.setPreviewSize(640, 352)
        self.rightCam.setCamera("right")
        self.rightCam.setResolution(self.COLOR_RESOLUTION)
        self.rightCam.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
        self.rightCam.setFps(self.FPS)

        # Center camera properties
        self.centerCam.setIspScale(2, 3)
        self.centerCam.setPreviewSize(640, 352)
        self.centerCam.setCamera("center")
        self.centerCam.setResolution(self.COLOR_RESOLUTION)
        self.centerCam.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
        self.centerCam.setFps(self.FPS)

        # Stereo properties
        self.stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.DEFAULT)
        self.stereo.initialConfig.setMedianFilter(dai.MedianFilter.MEDIAN_OFF)   #POST PROCESSING
        self.stereo.setLeftRightCheck(self.lr_check)
        self.stereo.setExtendedDisparity(self.extended_disparity)
        self.stereo.setSubpixel(self.subpixel)

        # Network specific settings
        self.detection.setConfidenceThreshold(self.confidenceThreshold)
        self.detection.setNumClasses(len(self.labelMap))
        self.detection.setCoordinateSize(4)
        self.detection.setIouThreshold(0.5)
        self.detection.setBlobPath(self.nnPath)
        self.detection.setNumInferenceThreads(2)
        self.detection.input.setBlocking(False)

        # Converter properties
        self.manip.initialConfig.setResize(640, 352)
        # Convert HWC to CHW using the ImageManip node
        self.manip.initialConfig.setCropRect(0, 0, 640, 352)
        self.manip.setFrameType(dai.ImgFrame.Type.BGR888p)  # Set output format to CHW

    def _linkStereo(self):
        # Link left and right cam output to depth input
        # Link stereo depth output to host
        self.leftCam.isp.link(self.stereo.left)
        self.rightCam.isp.link(self.stereo.right)
        self.stereo.depth.link(self.xoutDepth.input)

    def _linkNN(self):
        # Link left camera with yolo network, because stereo image is base on left cam
        self.leftCam.preview.link(self.manip.inputImage) # convert img to the correct format 
        self.manip.out.link(self.detection.input)
        if self.syncNN:
            self.detection.passthrough.link(self.xoutRgb.input)
        else:
            self.leftCam.preview.link(self.xoutRgb.input)

        # Link detection to yolo output stream
        self.detection.out.link(self.xoutYolo.input)

    def _initQueues(self):
        outputFrames= 4
        self.qRgb   = self.device.getOutputQueue(name="rgb",   maxSize=outputFrames, blocking=False)
        self.qDet   = self.device.getOutputQueue(name="yolo",    maxSize=outputFrames, blocking=False)
        self.qDepth = self.device.getOutputQueue(name="depth", maxSize=outputFrames, blocking=False)

    def getBuffers(self)  ->tuple:
        if self.syncNN:
            inRgb   = self.qRgb.get()
            inDepth = self.qDepth.get()
        else:
            while(True):
                inRgb   = self.qRgb.tryGet()
                inDepth = self.qDepth.tryGet()

                if(inRgb and inDepth):
                    break

        return (inRgb.getCvFrame(),inDepth.getCvFrame())

    def getDetection(self) ->dai.ImgDetections:
        """
        This message contains a list of detections, which contains 
        label, confidence, and the bounding box information (xmin, ymin, xmax, ymax)."""
        # TODO understand imgDetections object and how it perform when no object detected
        if self.syncNN:
            inDet = self.qDet.get()
        else:
            inDet = self.qDet.tryGet()
        return inDet.detections

    def startCapture(self):
        if not self.device:
            print("Device is not running!")
        else:
            print("Device is running.")
        print("Starting pipeline...")
        self._initPipleline()
        print("Pipeline initialized.")
        self._setProperties()
        self._linkNN()
        self._linkStereo()
        self.device.startPipeline(self.pipeline)
        print("Available output queues:", self.device.getOutputQueueNames())
        self._initQueues()

    
    def stopCapture(self):
        if self.device:
            self.device.close()

        self.device     = None
        self.pipeline   = None

    def switchModel(self,model_path:str):
        self.stopCapture()
        self.nnPath = model_path
        self.startCapture()
