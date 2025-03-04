"""Follow red, green buoys paht"""
from GNC.Nav_Core.info_core import infoCore
from GNC.Guidance_Core.waypointNav import waypointNav
from GNC.Control_Core.motor_core_new import MotorCore
from GNC.Guidance_Core.mission_helper import MissionHelper
import time
import math
class PathNav:
    def __init__(self):
        self.config     = MissionHelper().load_json(path="GNC/Guidance_Core/Config/barco_polo.json")
        self.info       = infoCore(modelPath=self.config["test_model_path"],labelMap=self.config["test_label_map"])
        self.motor      = MotorCore()
        self.wayPNav    = waypointNav()
        self.ang , self.dis = self.wayPNav.updateDelta()

        self.finalPos = () # some lat lon
        pass

    def run(self):
        while(self.dis>3):# change tolerance for end point
            _,detections = self.info.getInfo()
            # SIMPLE WAY
            def motorControl(pos):
                if pos>0.5:
                    self.motor.yaw(0.4,0.4,-0.4,-0.4)
                else:
                    self.motor.yaw(0.4,0.4, 0.4, 0.4)
            for object in detections:
                if(object["label"]=="red buoy"):
                    bbox = object["bbox"]
                    motorControl((bbox[0]+bbox[2])/2)
                elif(object["label"] == "green buoy"):
                    bbox = object["bbox"]
                    motorControl((bbox[0]+bbox[2])/2)
                else:
                    self.motor.surge(0.5,0.5,0.5,0.5)

            # MAP WAY
            
