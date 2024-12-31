"""
Here is what functions need to be in place:
- Based on two objects, find the midpoint between the two objects.
- Based on an object's dimensions on the screen, and given the known size of the object and focal length of the camera, 
find the lat, lon of the object. NOTE: Not sure if this file is the right place for this.
- Based on where obstacles are, calculate a path that utilizes straight lines in order to move to a given waypoint.
"""

import math
from typing import Tuple, Union

class mapHelper:
    def __init__(self):
        self.R = 631700 # Earth's radius in meters.

    def calculate_midpoint(self, point1 : Tuple[float, float], point2: Tuple[float , int]) -> Tuple[float, float]:
        """
        Return the midpoint of two points. Points will be in the form of (lat, lon).
        """
        lat_1, lon_1 = map(math.radians, point1)
        lat_2, lon_2 = map(math.radians, point2)

        Bx = math.cos(lat_2) * math.cos(lon_2 - lon_1)
        By = math.cos(lat_2) * math.sin(lon_2 - lon_1)

        lat_mid = math.atan2(
            math.sin(lat_1) + math.sin(lat_2),
            math.sqrt((math.cos(lat_1) + Bx)**2 + (By)**2)
        )
        lon_mid = lon_1 + math.atan2(By, math.cos(lat_1) + Bx)
        lat_mid, lon_mid = map(math.degrees, [lat_mid, lon_mid])

        lon_mid = (lon_mid + 180) % 360 - 180

        return (lat_mid, lon_mid)
    
    def calculate_heading_to_waypoint(self, current_point : Tuple[float, float], waypoint : Tuple[float, float]) -> float:
        curr_lat = current_point[0]
        curr_lon = current_point[1]
        waypoint_lat = waypoint[0]
        waypoint_lon = waypoint[1]

        curr_lat, curr_lon, waypoint_lat, waypoint_lon = map(math.radians, [curr_lat, curr_lon, waypoint_lat, waypoint_lon])
        dlon = waypoint_lon - curr_lon

        x = math.cos(waypoint_lat) * math.sin(dlon)
        y = math.cos(curr_lat) * math.sin(waypoint_lat) - math.sin(curr_lat) * math.cos(waypoint_lat) * math.cos(dlon)
        bearing = math.atan2(x, y)

        # Convert back to degrees and normalize.
        bearing = (math.degrees(bearing) + 360) % 360
        return bearing
    
    def calculate_waypoint_from_vector(self, current_point : Tuple[float, float], bearing : float, magnitude : float) -> Tuple[float, float]:
        curr_lat, curr_lon = map(math.radians, current_point)
        bearing = math.radians(bearing)
        angular_distance = magnitude/self.R

        waypoint_lat = math.asin(
            math.sin(curr_lat) * math.cos(angular_distance) + math.cos(curr_lat) * math.sin(angular_distance) * math.cos(bearing)
        )
        waypoint_lon = curr_lon + math.atan2(
            math.sin(bearing) * math.sin(angular_distance) * math.cos(curr_lat),
            math.cos(angular_distance) - (math.sin(curr_lat) * math.sin(waypoint_lat))
        )

        waypoint_lat, waypoint_lon = map(math.degrees, [waypoint_lat, waypoint_lon])
        return(waypoint_lat, waypoint_lon)
    
    def calculate_latitude_distance(self, lat_1 : float, lat_2 : float) -> float:
        lat1, lat2 = map(math.radians, [lat_1, lat_2])
        distance_latitude = self.R * abs(lat2 - lat1)
        return distance_latitude
    
    def calculate_longitude_distance(self, lon_1 : float, lon_2 : float, average_latitude : float) -> float:
        lon1, lon2, latitude = map(math.radians, [lon_1, lon_2, average_latitude])
        distance_longitude = self.R * abs(lon2 - lon1) * math.cos(latitude)
        return distance_longitude
    
    def haversine(self, point1 : Tuple[float, float], point2: Tuple[float, float]) -> float:
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        Returns distance in meters
        """
        # convert decimal degrees to radians
        lat1, lon1 = map(math.radians, [point1])
        lat2, lon2 = map(math.radians, [point2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return c * self.R
    
    def extend_vector(self, vector_tail : Tuple[float, float], curr_vector_head : Tuple[float, float], scale : float):
        curr_lat, curr_lon = map(math.radians, vector_tail)
        # curr_waypoint_lat, curr_waypoint_lon = map(math.radians, curr_vector_head)
        distance = self.haversine(vector_tail, curr_vector_head)
        scaled_distance = distance * scale
        angular_distance = scaled_distance/self.R

        bearing = self.calculate_heading_to_waypoint(vector_tail, curr_vector_head)
        bearing = math.radians(bearing)

        new_lat = math.asin(
            math.sin(curr_lat) * math.cos(angular_distance) + 
            math.cos(curr_lat) * math.sin(angular_distance) * math.cos(bearing)
        )

        new_lon = curr_lon + math.atan2(
            math.sin(bearing) * math.sin(angular_distance) * math.cos(curr_lat),
            math.cos(angular_distance) - math.sin(curr_lat) * math.sin(new_lat)
        )

        new_lat, new_lon = map(math.degrees, [new_lat, new_lon])

        return (new_lat, new_lon)







