from GNC.info_core import infoCore
from GNC.Guidance_Core.mission_helper import MissionHelper
from GNC.Control_Core import motor_core
from API.Util import gis_funcs 
import cv2
import numpy as np
import time

threshold = 100

"""***"""
config     = MissionHelper()
print("loading configs")
config     = config.load_json(path="GNC/Guidance_Core/Config/barco_polo.json")
info       = infoCore(modelPath=config["sign_model_path"],labelMap=config["sign_label_map"])
print("start background threads")
info.start_collecting()
motor      = motor_core.MotorCore("/dev/ttyACM2",debug=False) # load with default port "/dev/ttyACM2"
time.sleep(2)
print("rest 2 seconds")
GPS, _ = info.getInfo()
calc_lat, calc_lon = gis_funcs.destination_point(GPS.lat, GPS.lon, GPS.heading, 15)