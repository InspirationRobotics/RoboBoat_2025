from API.GPS.gps_api import GPS

gps = GPS(serialport='/dev/ttyUSB0')

gps.calibrate_heading_offset()
