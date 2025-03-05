# from API.GPS.gps_api import GPS, GPSData

# import time
# import re

# class WaypointLogger:
#     def __init__(self, lat, lon, heading):
#         self.lat = lat
#         self.lon = lon
#         self.heading = heading

#     def parse_coordinates(self, fstring):
#         # Use regex to extract latitude and longitude
#         match = re.search(r"Lat: ([\d\.\-]+), Lon: ([\d\.\-]+)", fstring)
#         if match:
#             lat, lon = match.groups()
#             return float(lat), float(lon)
#         return None

#     def save_waypoint(self, filename="waypoints.txt"):
#         with open(filename, "w") as file:
#             file.write(f"{self.lat}, {self.lon}\n")

# # Example usage
# waypoint = WaypointLogger(0, 0, 90)
# fstring_output = f"Lat: {waypoint.lat}, Lon: {waypoint.lon}, Heading: {waypoint.heading}"

# # Parse coordinates
# lat_lon = waypoint.parse_coordinates(fstring_output)
# if lat_lon:
#     print(f"Extracted Coordinates: {lat_lon}")
#     waypoint.save_waypoint()
# else:
#     print("Failed to extract coordinates.")



# def log_gps():
#     # log = open(f'Test_Scripts/API_Tests/GPS_Tests/GPSLogs/GPSlog_{int(time.time())}.txt', "w")
#     log = open(f'GNC/Guidance_Core/Config/waypoints.txt', "w")

#     def callback(data : GPSData):
#         parsed_lat_lon = ()
#         log.write(str(data) + '\n')

#     gps = GPS('/dev/ttyUSB0', 115200, callback=callback)

#     rate = 2 # Period
#     print(f"Beginning logging process @ one waypoint every {rate} seconds")
#     while True:
#         try:
#             time.sleep(rate)
#         except KeyboardInterrupt:
#             break

#     del gps
#     log.close()

# if __name__ == "__main__":
#     # To test print ability
#     # print_gps()

    
#     # To test log ability
#     log_gps()

import re
import time
from  API.GPS.gps_api import GPS, GPSData  # Ensure you import the correct GPS module

def log_gps():
    # Open the log file for writing waypoints
    log = open(f'GNC/Guidance_Core/Config/waypoints.txt', "w")

    def parse_coordinates(gps_string):
        """Extract latitude and longitude from a GPS data string."""
        match = re.search(r"Lat: ([\d\.\-]+), Lon: ([\d\.\-]+)", gps_string)
        if match:
            lat, lon = match.groups()
            return float(lat), float(lon)
        return None

    def callback(data: GPSData):
        """Callback function to process incoming GPS data."""
        gps_string = f"Lat: {data.lat}, Lon: {data.lon}, Heading: {data.heading}"
        log.write(gps_string + '\n')  # Log raw GPS data

        parsed_lat_lon = parse_coordinates(gps_string)
        if parsed_lat_lon:
            lat, lon = parsed_lat_lon
            log.write(f"{lat}, {lon}\n")  # Save lat, lon as waypoints

    gps = GPS('/dev/ttyUSB0', 115200, callback=callback)

    rate = 2  # Period in seconds
    print(f"Beginning logging process @ one waypoint every {rate} seconds")
    
    try:
        while True:
            time.sleep(rate)
    except KeyboardInterrupt:
        print("Logging interrupted. Closing file.")
    finally:
        del gps
        log.close()

if __name__ == "__main__":
    log_gps()