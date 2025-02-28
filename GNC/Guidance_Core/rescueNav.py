"""For rescue delivery"""
from GNC.Nav_Core.info_core import infoCore
from GNC.Guidance_Core.waypointNav import waypointNav
from GNC.Control_Core.motor_core_new import MotorCore
from GNC.Guidance_Core.mission_helper import MissionHelper
from API.Servos import mini_maestro
import time
import math

class Rescue:
    def __init__(self):
        self.config     = MissionHelper().load_json(path="GNC/Guidance_Core/Config/barco_polo.json")
        self.info       = infoCore(modelPath=self.config["test_model_path"],labelMap=self.config["test_label_map"])
        self.motor      = MotorCore()
        self.wayPNav    = waypointNav()
        self.servo = mini_maestro.MiniMaestro(self.servo_port)

    def 