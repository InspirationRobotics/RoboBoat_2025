"""
Sandbox file to make it convenient to see how code works/experiment with syntax.
Can be deleted whenever someone feels like cleaning up.
"""

from API.GPS.waypoint_data_parser import GPSDataParser
file_path =  r'Test_Scripts/API_Tests/GPS_Tests/missions/GPS_Parser_Test.txt'
dp = GPSDataParser(file_path)
position, heading = dp.parse_data()
lat, lon = position[next(iter(position))]
print(lat, lon)