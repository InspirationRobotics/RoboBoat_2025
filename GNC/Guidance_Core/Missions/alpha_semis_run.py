"""
Mission run for Semi-Final Course on Alpha.
Includes Nav Channel (via waypoint), Follow the Path (FTP)
"""

import math
import time
import threading
import numpy as np

from GNC.Nav_Core import gis_funcs
from GNC.Nav_Core.info_core import infoCore
from GNC.Control_Core  import motor_core_new
from GNC.Guidance_Core import mission_helper, waypointNav
from GNC.Guidance_Core.Missions import navChannel, FTP

from API.Servos.mini_maestro import MiniMaestro


config     = mission_helper.MissionHelper()
print("Loading configs...")
config     = config.load_json(path="GNC/Guidance_Core/Config/barco_polo.json")
info       = infoCore(modelPath=config["MHS_SEALS_MODELV14"])
print("Starting background threads...")
info.start_collecting()
motors      = motor_core_new.MotorCore("/dev/ttyACM2", debug=True) # load with default port "/dev/ttyACM2"
FTP_mission    = FTP.FTP(infoCore=info, motors=motors)

# Calculate initial point, NAV channel waypoint, Return to Home (RTH) waypoint.
mission = navChannel.navChannel(infoCore=info, motors=motors)
lat, lon = mission.run()
nav_lat, nav_lon = gis_funcs.destination_point(lat, lon, 270, 32)
return_lat, return_lon = gis_funcs.destination_point(lat, lon, 0, 25)

# Initial point
first_point = {"lat" : lat, "lon" : lon}
# Point on other end of NAV
nav_point = {"lat" : nav_lat, "lon" : nav_lon}
# Point near the black buoy gates
return_point = {"lat" : return_lat, "lon" : return_lon}

NNAV = waypointNav(infoCore=info, motors=motors)
tolerance = 1.5

def start_waypoint(point, tolerance : float = 1.0):
    nav_thread = threading.Thread(target=NNAV.run, args=(point, tolerance), daemon=True) # arguemnets: waypoint(dict), tolerance(float)->in meters
    nav_thread.start()
    nav_thread.join()
    print("[Mission] Waypoint reached.")

try:
    start_waypoint(nav_point)
    FTP_mission.run(tolerance=1.5)
    start_waypoint(return_point)
    start_waypoint(first_point)
    FTP_mission.stop()
except KeyboardInterrupt:
    FTP_mission.stop()