from GNC.Nav_Core import gis_funcs
class FTP:
    def __init__(self, *, infoCore, motors):
        self.info = infoCore
        self.motors = motors

        # Threshold to look for objects.
        self.threshold = 0.7

        self.cur_ang = None
        self.cur_dis = None

    def updateDelta(self,lat,lon):
        gpsdata = self.info.getGPSData()
        print(f"waypoints| lat: {lat} | lon: {lon}")
        self.cur_ang =  gis_funcs.relative_bearing(lat1=gpsdata.lat,lon1=gpsdata.lon,lat2=lat,lon2=lon,current_heading=gpsdata.heading)
        self.cur_dis =  gis_funcs.haversine(lat1=gpsdata.lat,lon1=gpsdata.lon,lat2=lat,lon2=lon) # this return angle to the range (-180,180)
        print(f"abs head: {gpsdata.heading} | lat: {gpsdata.lat} | lon: {gpsdata.lon}")
        print(f"delta ang: {self.cur_ang} | delta dis: {self.cur_dis}")
        # normalize angle to value between 0 and 1
        self.cur_ang /= 180
        return self.cur_ang, self.cur_dis
    
    def run(self,endpoint,tolerance=1.5):
        # Find the two closest objects that are lowest on the screen.
        # Find the midpoint of both objects(pixel values).
        # If the difference between one midpoint is greater than the other, yaw to force the values to be within equal within a certain 
        # tolerance (while always moving forward)
        # Always move forward while yawing
        gpsData, detections = self.info.getInfo()
        
        self.cur_ang,self.cur_dis = self.updateDelta(gpsData.lat,gpsData.lon)
        while self.end == False:
            gpsData, detections = self.info.getInfo()
            # Find the lowest two detections.
            # Going down the screen will actually increase the value, so lowest will be 1.
            # Going across the screen decreases the value (xmax -> xmin).

            # Find the lowest of each type.
            # Types are "green", "red", "yellow", "cross", "triangle"
            # "bbox": (detection.xmin, detection.ymin, detection.xmax, detection.ymax)

            red_object_list = []
            green_object_list = []

            # collect objects
            for detection in detections:
                if detection["type"] == "green_buoy" or detection["type"] == "green_pole_buoy":
                    green_object_list.apend(detection)

                if detection["type"] == "red_buoy" or detection["type"] == "red_pole_buoy" and detection["bbox"][2] < self.threshold:
                    red_object_list.append(detection)

            # find min
            red_min = 0
            red_min_detection = None
            green_min = 0
            green_min_detection = None

            for object in red_object_list:
                if(object["bbox"][3]>red_min):
                    red_min_detection = object
            for object in green_object_list:
                if(object["bbox"][3]>green_min):
                    green_min_detection = object

            # find midpoint
            red_center      = red_min_detection["bbox"][0] + red_min_detection["bbox"][2]
            green_center    = green_min_detection["bbox"][0] + green_min_detection["bbox"][2]
            path_center     = (red_center + green_center)/2

            # control the motor
            delta_center = path_center - 0.5
            if(delta_center>40):
                """turn left"""
                self.motors.veer(0.8,-0.5)
            elif(delta_center<-40):
                """turn right"""
                self.motors.veer(0.8, 0.5)

            # update del dis
            self.cur_ang,self.cur_dis = self.updateDelta(gpsData.lat,gpsData.lon)

            # check stop statement 
            if(self.cur_dis < tolerance):
                print("FTP finished")
                break


            



