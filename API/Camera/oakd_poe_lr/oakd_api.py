"""
WORK IN PROGRESS
This is the api for setting up pipleine for oakd LR camera
Example api format: https://discuss.luxonis.com/d/4702-capture-color-and-depth-only-on-event/8 
"""
import json
import time
import random
import cv2
import numpy as np
import depthai as dai
from typing import Tuple
from datetime import timedelta

class OAKD_LR:
    def __init__(self):
        # set up pipeline
        pass

    def Link_Stereo(self):
        # link left and right camera for stereo
        pass

    def Link_NN(self):
        # deploy nn on left camera, because the stereo is base on left cam
        pass
    
