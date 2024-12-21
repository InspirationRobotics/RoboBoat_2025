from API.GPS.gps_api import GPS, GPSData

def callback(data : GPSData):
    pass

gps = GPS('/dev/ttyUSB0', 115200, callback=callback, offset=270.96788823529414)
gps.save_waypoints()