from GNC.Control_Core  import motor_core_new
from GNC.Nav_Core.info_core import infoCore
import GNC.Nav_Core.gis_funcs as gpsfunc
from GNC.Guidance_Core import waypointNav
from GNC.Guidance_Core.mission_helper import MissionHelper
from GNC.Guidance_Core.Missions import navChannel
import threading
import math
import time

config     = MissionHelper()
data     = config.load_json(path="GNC/Guidance_Core/Config/barco_polo.json")
config.parse_config_data(data)
print("[MISSION] Loaded configuration.")

info       = infoCore(config.model_path, config.model_label_map)
print("[MISSION] Starting background threads.")
info.start_collecting()
motors     = motor_core_new.MotorCore(config["motor_port"]) 

mission = navChannel.navChannel(infoCore=info, motors=motors)
