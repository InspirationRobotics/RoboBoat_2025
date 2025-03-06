from GNC.Nav_Core import gis_funcs

class navChannel:
    def __init__(self, *, infoCore, motors):
        self.info = infoCore
        self.motors = motors
        self.distance = 35 # How far to move from the initial position (meters)

    def run(self):
        currentGPSData, _ = self.info.getInfo()
        currLat, currLon, currHeading = (currentGPSData.lat, currentGPSData.lon, currentGPSData.heading)
        calc_lat, calc_lon = gis_funcs.destination_point(currLat, currLon, 270, self.distance)
        return calc_lat, calc_lon
    
        
        



