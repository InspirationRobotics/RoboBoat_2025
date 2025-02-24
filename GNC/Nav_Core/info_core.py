"""
This script meant to collect information from gps and perception, and start background threads
"""

from API.GPS.gps_api import GPS, GPSData
from Perception.Perception_Core.perception_core import CameraCore

from threading import Thread, Lock
from queue import Queue

class infoCore:
    def __init__(self):
        self.stop_event = None
        self.GPS = GPS(serialport = "/dev/ttyUSB0", baudrate= 115200, callback = None, threaded= True, offset = -81)

    
    

