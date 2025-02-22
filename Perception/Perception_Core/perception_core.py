"""
WORK IN PROGRESS
Here will be all of the perception core code.
Link to source file: https://github.com/InspirationRobotics/RX24-perception/blob/main/perception/perception_core/perception.py
"""
from threading import Thread, Lock
from multiprocessing import Process, Value
import numpy as np
from API.Camera.oakd_poe_lr.oakd_api import OAKD_LR
import cv2
import math

# TODO figure out threading, the program is unacceptably slow
class Camera:
    def __init__(self,model_path:str, labelMap:list):
        self.cam        = OAKD_LR(model_path=model_path, labelMap=labelMap)
        self.cam_lock   = Lock()
        self.labelMap   = labelMap

        # cv frame from camera
        # Rgb and Depth are cv frame, Det is list containing object information
        self.Rgb    = None
        self.Det    = None
        self.Depth  = None

        pass
    
    def _info(self,message:str):
        """
        Utility function to notify the user of information pertaining to a specific camera.

        Args:
            message (str): Message to print out to terminal.
        """
        print(f"OAK_D LR Info: {message}")
    def _getView(self):
        self.Rgb,self.Depth = self.cam.getBuffers()
        return self.Rgb, self.Depth
    
    def __frameNorm(self,frame, bbox):
            normVals = np.full(len(bbox), frame.shape[0])
            normVals[::2] = frame.shape[1]
            return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)

    def start(self):
        self.cam_thread = Thread(target=self.cam.startCapture)
        self.cam_thread.start()
        self._info("Camera capture started")

    def stop(self):
        try:
            self.cam_thread.join()
        except:
            self._info("Failed to stop thread")
            return
        self._info("Camera thread stopped")

    def getObjectDepth(self, scale:float = 0.5) ->list:
        """This function get the depth of detected object and return them"""
        # TODO Test smaller bbox and depth accuracy
        detections = self.cam.getDetection()
        result = []
        
        # TODO ask what kind of bbox we need, do we need percentage or exact pixels?
        scale_value = scale # the size of the center bbox for finding the average depth

        for detection in detections:
            width       = math.abs(detection.xmax - detection.xmin)
            height      = math.abs(detection.ymax - detection.ymin)
            center_x    = (detection.xmax + detection.xmin)/2
            center_y    = (detection.ymax + detection.ymin)/2

            # The original bbox
            bbox_full   = self.__frameNorm(self.Depth, (detection.xmin, detection.ymin, detection.xmax, detection.ymax))
            
            # Smaller bbox for depth calculation
            
            bbox_cetner = self.__frameNorm(self.Depth, (center_x-width*scale_value/2, center_y-height*scale_value/2, center_x+width*scale_value/2, center_y+height*scale_value/2))
            depth_crop = self.Depth[bbox_cetner[1]:bbox_cetner[3], bbox_cetner[0]:bbox_cetner[2]]
            avg_depth = np.mean(depth_crop) if depth_crop.size > 0 else 0  # Handle empty crop cases
            
            # Add information to return
            result.append(
                {
                    "label": detection.label, # this is the index of the object on label map
                    "bbox" : self.__frameNorm(self.Depth,(detection.xmin, detection.ymin, detection.xmax, detection.ymax)),
                    "depth": avg_depth/1000 # original in mm, convert to meters
                }
            )
        
        return result
    

    def visualize(self):
        """This return a labeled cv2 frame for visualizaiton"""
        RGB, DEPTH = self._getView()
        if(RGB is None):
            return None
        color = (255, 0, 0)
        try:
            for detection in self.cam.getDetection():
                # TODO: Investigate into the label index.
                # print(f"label index: {detection.label}")
                bbox = self.__frameNorm(RGB, (detection.xmin, detection.ymin, detection.xmax, detection.ymax))
                # print(bbox)
                cv2.putText(RGB, self.labelMap[detection.label], (bbox[0] + 10, bbox[1] + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)  # I added -1 because the label is one whne I only have one detect object
                cv2.putText(RGB, f"{int(detection.confidence * 100)}%", (bbox[0] + 10, bbox[1] + 40), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
                cv2.rectangle(RGB, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
        except Exception as e:
            print(f"Failed to detect Error: {e}")

        return RGB
    
        