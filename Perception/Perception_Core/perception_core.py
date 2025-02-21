"""
WORK IN PROGRESS
Here will be all of the perception core code.
Link to source file: https://github.com/InspirationRobotics/RX24-perception/blob/main/perception/perception_core/perception.py
"""
from threading import Thread, Lock
from multiprocessing import Process, Value
import numpy as np
from API.Camera.oakd_poe_lr.oakd_api import OAKD_LR


class Camera:
    def __init__(self,model_path:str, labelMap:list):
        self.cam        = OAKD_LR(model_path=model_path, labelMap=labelMap)
        self.cam_lock   = Lock()
        self.labelMap   = labelMap

        # cv frame from camera
        self.Rgb,self.Det,self.Depth = None
        # Rgb and Depth are cv frame, Det is list containing object information

        # 
        pass
    
    def _info(self,message:str):
        """
        Utility function to notify the user of information pertaining to a specific camera.

        Args:
            message (str): Message to print out to terminal.
        """
        print(f"OAK_D LR Info: {message}")
    def _getView(self):
        self.inRgb,self.inDepth = self.cam.getBuffers()
    
    def __frameNorm(self,frame,bbox):
        # bounding box, value from 0~1 tl->top left | bl->buttom left bbox=(tlx,tly,blx,bly)
        # We are converting the bbox values from percentage to pixels
        normVals = np.full(len(bbox), frame.shape[0])
        normVals[::2] = frame.shape[1]
        return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)

    def start(self):
        self.cam_thread = Thread(target=self.cam.startCapture())
        self.cam_thread.start()
        self._info("Camera capture started")

    def stop(self):
        try:
            self.cam_thread.join()
        except:
            self._info("Failed to stop thread")
            return
        self._info("Camera thread stopped")

    def getObjectDepth(self) ->list:
        """This function get the depth of detected object and return them"""
        detections = self.cam.getDetection()

        result = []
        # TODO ask what kind of bbox we need, do we need percentage or exact pixels?
        for detection in detections:
            result.append(
                {
                    "label": detection.label, # this is the index of the object on label map
                    "bbox" : self.frameNorm(self.Depth,(detection.xmin, detection.ymin, detection.xmax, detection.ymax)) 
                }
            )
        
        return result
    
        