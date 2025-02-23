from API.GPS.gps_api import GPS

gps = GPS(serialport='/dev/ttyUSB0')

GPS.calibrate_heading_offset()
