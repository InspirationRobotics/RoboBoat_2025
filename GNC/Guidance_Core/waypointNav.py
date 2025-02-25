"""
This is the script for waypoint navigation
"""
from GNC.Control_Core.motor_core_new  import MotorCore
from GNC.Nav_Core.info_core import infoCore
from GNC.Guidance_Core.mission_helper import MissionHelper
import GNC.Nav_Core.gis_funcs as gpsfunc

class waypointNav:
    def __init__(self):
        self.config             = MissionHelper()
        self.info               = infoCore()
        self.motor              = MotorCore() # load with default port "/dev/ttyACM2"

        self.waypoints :list    = None
        
        self.cur_ang            = None
        self.cur_dis            = None
        pass

    def _loadConfig(self,path:str):
        self.config.parse_config_data(self.config.load_json(path="GNC/Guidance_Core/Config/barco_polo.json"))

    def _loadWaypoints(self) ->list:
        pass

    def _controlLoop(self):
        pass

    def start(self):
        self.info.start_collecting()
        print("Background Threads started")

    def stop(self):
        self.info.stop_collecting()
        print("Background Threads stopped")

    def run(self):
        angleTolerance = 5      # 5 degrees tolerance
        distanceTolerance = 3   # 3 meters tolerance

        for points in self.waypoints:
            lat = points[0]
            lon = points[1]
        
            # update bearing angle and distance
            self.updateDelta(lat=lat, lon=lon)

            while(self.cur_dis>distanceTolerance):
                # set max motor power pwm
                MAXFRONT    = 1750
                MAXBACK     = 1600

                # convert bearing angle to vector
                delta_ang = 180-self.cur_ang

                # yaw base on angle and distance
                self.motor.yaw(MAXFRONT,MAXFRONT,MAXBACK)



        pass

    def updateDelta(self,lat,lon):
        gpsdata = self.info.getGPSData
        self.cur_ang =  gpsfunc.relative_bearing(lat1=gpsdata.lat,lon1=gpsdata.lon,lat2=lat,lon2=lon,current_heading=gpsdata.heading)
        self.cur_dis =  gpsfunc.haversine(lat1=gpsdata.lat,lon1=gpsdata.lon,lat2=lat,lon2=lon)


# load waypoints (for testing)



# Start infoCore
info_core = infoCore()
info_core.start_collecting()


