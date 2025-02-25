"""
This is the script for waypoint navigation
"""
from GNC.Control_Core.motor_core_new  import MotorCore
from GNC.Nav_Core.info_core import infoCore
from GNC.Guidance_Core.mission_helper import MissionHelper
import GNC.Nav_Core.gis_funcs as gpsfunc
import math

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

    def start(self):
        self.info.start_collecting()
        print("Background Threads started")

    def stop(self):
        self.info.stop_collecting()
        print("Background Threads stopped")

    def run(self):
        angleTolerance = 5.0/180    # 5 degrees tolerance  (I think we don't need this)
        distanceTolerance = 3       # 3 meters tolerance

        for points in self.waypoints:
            lat = points[0]
            lon = points[1]
        
            # update bearing angle and distance
            self.updateDelta(lat=lat, lon=lon)

            while(self.cur_dis>distanceTolerance):
                # set max motor power pwm
                MAXFRONT    = 0.6
                MAXBACK     = 0.4

                # Equation: 0.58(e^x-1) why? when x=0,y=0, when x =1 y ~= 1
                turningPower = MAXBACK * (0.58*(math.exp(self.cur_ang)-1))
                
                # Equation: -0.73e^x +2 why? when x=0, y=1, x=1, y~=0
                thrusterPower = MAXFRONT * ((-0.73)*(math.exp(self.cur_ang)) + 2)

                # yaw base on angle and distance
                # apply expoential relationship for turning power and angle
                self.motor.yaw(MAXFRONT,MAXFRONT,turningPower,turningPower)

    def updateDelta(self,lat,lon):
        gpsdata = self.info.getGPSData
        self.cur_ang =  gpsfunc.normalized_bearing_bearing(lat1=gpsdata.lat,lon1=gpsdata.lon,lat2=lat,lon2=lon,current_heading=gpsdata.heading)
        self.cur_dis =  gpsfunc.haversine(lat1=gpsdata.lat,lon1=gpsdata.lon,lat2=lat,lon2=lon) # this return angle to the range (-180,180)
        # normalize angle to value between 0 and 1
        self.cur_dis /= 180



