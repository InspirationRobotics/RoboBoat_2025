"""
This is the script for waypoint navigation
"""
from GNC.Control_Core  import motor_core_new
from GNC.Nav_Core.info_core import infoCore
from GNC.Guidance_Core.mission_helper import MissionHelper
import GNC.Nav_Core.gis_funcs as gpsfunc
import math
import time

class waypointNav(MissionHelper):
    def __init__(self, *, info = None, motor = None):              
        data = self.load_json(config)
        self.parse_config_data(data)

        if info is None:
            self.info               = infoCore(modelPath=self.sign_model_path, labelMap=self.sign_label_map)
        else:
            self.info = info
        if motor is None:
            self.motor              = motor_core_new(self.motor_port)
        else:
            self.motor              = motor

        self.waypoints :list    = None
        
        self.cur_ang            = None
        self.cur_dis            = None


    def _loadConfig(self,file_path:str = "GNC/Guidance_Core/Config/barco_polo.json"):
        self.parse_config_data(self.load_json(path=file_path))

    def _loadWaypoints(self):
        print(f"path: {self.waypoint_file}")
        self.waypoints = self.__readLatLon(self.waypoint_file)
        print("\nWaypoints: ")
        for points in self.waypoints:
            print(points)

    def loadWaypoints(self,points):
        """This is used when waypoint nav is not readed from txt"""
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
        # load waypoints
        print("Loading waypoints...")
        self._loadWaypoints()



    def stop(self):
        self.info.stop_collecting()
        print("Background Threads stopped")
        self.motor.stop()
        print("Motors stoped")

    def run(self,tolerance:int = 1.5):
        """Main logic of waypoint navigation"""
        angleTolerance = 5.0/180    # 5 degrees tolerance  (I think we don't need this)
        distanceTolerance = tolerance       # 3 meters tolerance

        for points in self.waypoints:
            
            latin = points["lat"]
            lonin = points["lon"]
        
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
                turningPower = MAXBACK * self.cur_ang
                
                # Equation: 1-|x^0.2| why? concave up and decreasing as angle increase
                # TODO I think we need to add another varaible to slow down when distance is smaller
                thrusterPower = MAXFRONT * (1 - abs(math.pow(abs(self.cur_ang), 3))) * (self.cur_dis / (initDis-distanceTolerance))
                # yaw base on angle and distance
                # apply expoential relationship for turning power and angle
                self.motor.yaw(thrusterPower,turningPower)
                # 0.1 s interval
                time.sleep(0.01)

                # update information
                self.updateDelta(lat=latin, lon=lonin)
            
            print("wapoint reached")

        print("All points reached")

    def updateDelta(self,lat,lon):
        gpsdata = self.info.getGPSData()
        print(f"waypoints| lat: {lat} | lon: {lon}")
        self.cur_ang =  gpsfunc.relative_bearing(lat1=gpsdata.lat,lon1=gpsdata.lon,lat2=lat,lon2=lon,current_heading=gpsdata.heading)
        self.cur_dis =  gpsfunc.haversine(lat1=gpsdata.lat,lon1=gpsdata.lon,lat2=lat,lon2=lon) # this return angle to the range (-180,180)
        print(f"abs head: {gpsdata.heading} | lat: {gpsdata.lat} | lon: {gpsdata.lon}")
        print(f"delta ang: {self.cur_ang} | delta dis: {self.cur_dis}")
        # normalize angle to value between 0 and 1
        self.cur_ang /= 180
        return self.cur_ang, self.cur_dis



if __name__ == "__main__":
    config     = MissionHelper()
    print("loading configs")
    config.load_json(path="GNC/Guidance_Core/Config/barco_polo.json")
    info       = infoCore(modelPath=config["sign_model_path"],labelMap=config["sign_label_map"])
    print("start background threads")
    info.start_collecting()
    motor      = motor_core_new.MotorCore("/dev/ttyACM2") # load with default port "/dev/ttyACM2"

    mission    = waypointNav(info=info, motor=motor)
    mission.start()
    try:
        mission.run()
        mission.stop()
    except KeyboardInterrupt:
        mission.stop()
