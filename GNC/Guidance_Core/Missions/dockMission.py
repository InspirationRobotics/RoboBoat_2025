from GNC.Control_Core  import motor_core_new
from GNC.Nav_Core.info_core import infoCore
from GNC.Guidance_Core.mission_helper import MissionHelper
import GNC.Nav_Core.gis_funcs as gpsfunc
import threading
import math
import time
from API.Servos.mini_maestro import MiniMaestro
from GNC.Guidance_Core.waypointNav import waypointNav
try:
    config     = MissionHelper()
    print("loading configs")
    config     = config.load_json(path="GNC/Guidance_Core/Config/barco_polo.json")
    info       = infoCore(modelPath=config["sign_model_path"],labelMap=config["sign_label_map"])
    print("start background threads")
    info.start_collecting()
    motor      = motor_core_new.MotorCore("/dev/ttyACM2") # load with default port "/dev/ttyACM2"
    mission    = waypointNav(infoCore=info, motors=motor)

    waypoints  = mission._readLatLon(file_path = config["waypoint_file"])
        

    nav_thread = threading.Thread(target=mission.run, args=(waypoints[0], 1.0), daemon=True)
    nav_thread.start()
    nav_thread.join()  # ✅ WAIT for thread to finish before stopping motors

    nav_thread = threading.Thread(target=mission.run, args=(waypoints[1], 1.0), daemon=True)
    nav_thread.start()
    nav_thread.join()  # ✅ WAIT for thread to finish before stopping motors


    motor.surge(-1)
    time.sleep(60)

    mission.stop()
    print("program ended")
except:
    print("ending...")
    mission.stop()

    