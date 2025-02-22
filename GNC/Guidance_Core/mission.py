import time
import json
from GNC.Control_Core import motor_core
from GNC.Nav_Core import nav_path
from GNC.Guidance_Core.mission_helper import MissionHelper

class Mission(MissionHelper):
    def __init__(self, *, config : str = "GNC/Guidance_Core/Config/barco_polo.json"):
        data = self.load_json(config)
        self.parse_config_data(data)

        self.motors = motor_core.MotorCore(self.motor_port, self.gps_port)
        self.mission_path = nav_path.Nav_Path(read_waypoints=self.read_waypoints, waypoint_file=self.waypoint_file, 
                                              use_map=self.use_map, map_file=self.map_file)
        
        self.end = False

    def run(self):
        while True:
            if self.end == True:
                break
            if self.motors.target_reached == True:
                waypoint = self.mission_path.read_file()
                self.motors.desired_position = waypoint
                if waypoint is None:
                    print("Waypoint run complete.")
                    self.end = True
                print(waypoint)
            else:
                continue
            time.sleep(0.2)