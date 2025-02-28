"""
This is the script for waypoint navigation
"""
from GNC.Control_Core.motor_core_new  import MotorCore
from GNC.Nav_Core.info_core import infoCore
from GNC.Guidance_Core.mission_helper import MissionHelper
import GNC.Nav_Core.gis_funcs as gpsfunc
import math
import time

class waypointNav:
    def __init__(self):
        self.config             = MissionHelper()
        print("Loading Config file ...")
        self._loadConfig()                 

        self.info               = infoCore(modelPath=self.config.model_path,labelMap=self.config.label_map)
        self.motor              = MotorCore() # load with default port "/dev/ttyACM2"

        self.waypoints :list    = None
        
        self.cur_ang            = None
        self.cur_dis            = None


    def _loadConfig(self,file_path:str = "GNC/Guidance_Core/Config/barco_polo.json"):
        self.config.parse_config_data(self.config.load_json(path=file_path))

    def _loadWaypoints(self):
        print(f"path: {self.config.waypoint_file}")
        self.waypoints = self.__readLatLon(self.config.waypoint_file)
        print("\nWaypoints: ")
        for points in self.waypoints:
            print(points)

    def loadWaypoints(self,points):
        """This is used when waypoint nav is not reading waypoint"""
        self.waypoints = list(points)
        pass

    def __readLatLon(self,file_path:str)->list:
        lat_lon_list = []
    
        with open(file_path, 'r') as file:
            for line in file:
                lat, lon = map(float, line.strip().split(','))
                lat_lon_list.append({'lat': lat, 'lon': lon})
        
        return lat_lon_list

    def start(self):
        # start info core and load config
        print("Starting background Threads...")
        self.info.start_collecting()

        # load waypoints
        print("Loading waypoints...")
        self._loadWaypoints()



    def stop(self):
        self.info.stop_collecting()
        print("Background Threads stopped")

    def run(self):
        """Main logic of waypoint navigation"""
        angleTolerance = 5.0/180    # 5 degrees tolerance  (I think we don't need this)
        distanceTolerance = 3       # 3 meters tolerance

        for points in self.waypoints:
            
            latin = points[0]
            lonin = points[1]
        
            # update bearing angle and distance
            self.updateDelta(lat=latin, lon=lonin)
            
            # store current distance
            initDis = self.cur_dis

            while(self.cur_dis>distanceTolerance):
                # set max motor power pwm
                MAXFRONT    = 0.8
                MAXBACK     = 0.5

                # TODO test different graph and its impact on the performance, 
                # Try ^2.5 for turning power
                # Try ^0.4 for thruster power
                # Equation: x^3 why? Higher turning power at a greater angle, decreases as angle decreases, also can be + or - depend on angle
                turningPower = MAXBACK * (math.pow(self.cur_ang,3))
                
                # Equation: 1-|x^0.2| why? concave up and decreasing as angle increase
                # TODO I think we need to add another varaible to slow down when distance is smaller
                thrusterPower = MAXFRONT * (1-abs(math.pow(self.cur_ang,0.2))) * (math.pow((self.cur_dis/initDis),2))

                # yaw base on angle and distance
                # apply expoential relationship for turning power and angle
                self.motor.yaw(thrusterPower,thrusterPower,turningPower,turningPower)

                # 0.1 s interval
                time.sleep(0.1)

                # update information
                self.updateDelta(lat=latin, lon=lonin)

    def updateDelta(self,lat,lon):
        gpsdata = self.info.getGPSData
        self.cur_ang =  gpsfunc.normalized_bearing_bearing(lat1=gpsdata.lat,lon1=gpsdata.lon,lat2=lat,lon2=lon,current_heading=gpsdata.heading)
        self.cur_dis =  gpsfunc.haversine(lat1=gpsdata.lat,lon1=gpsdata.lon,lat2=lat,lon2=lon) # this return angle to the range (-180,180)
        # normalize angle to value between 0 and 1
        self.cur_dis /= 180

        return self.cur_ang, self.cur_dis



if __name__ == "__main__":
    mission = waypointNav()
    mission.start()
    mission.run()
