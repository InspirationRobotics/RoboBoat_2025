"""
This is a manager class
This script meant to collect information from gps and perception, and start background threads
"""

from API.GPS.gps_api import GPS, GPSData
from Perception.Perception_Core.perception_core import CameraCore

from threading import Thread, Lock
from queue import Queue

class infoCore:
    def __init__(self,modelPath:str ,labelMap:list):
        # Stop event to control the manager core and background threads
        self.manager_stop_event = None
        
        # Initialize GPS and Camera
        self.Camera = CameraCore(model_path=modelPath,labelMap=labelMap)

    def start_collecting(self):
        # A Thread is started when you initialize the GPS object
        self.GPS = GPS(serialport = "/dev/ttyUSB0", baudrate= 115200, callback = None, threaded= True, offset = -81) 
        self.Camera.start()   # Start Perception Thread
        pass

    def stop_collecting(self):
        self.GPS.__del__()
        self.Camera.stop()

    def getDetection(self) ->list: # return detection & depth information
        return self.Camera.get_object_depth()  
    
    def getGPSData(self) ->GPSData:
        return self.GPS.get_data()





    
    

