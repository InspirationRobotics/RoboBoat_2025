"""
Planning:
- Need a map which we can plot points on and calculate waypoints effectively.
- Coordinates will be absolute, not relative to initial starting point.
- Each object plotted needs three things: type of object, latitude, and longitude.
- The map should be a list of objects. It is more to store and visualize the positions of objects than anything else.

This map will be not be complete during a competition run unless we have made it through the full course.
NOTE: We may be able to create two maps -- one that is preconfigured through surveying, and contains all of the mission obstacles/elements, 
and the other being the one that is created as we come across obstacles via computer vision.
"""

import json
from typing import Tuple, Union
from pathlib import Path
from GNC.Nav_Core.mapHelper import mapHelper
import math

class Object:
    def __init__(self, /, object_type : str = None, latitude : float = None, longitude : float = None, confidence : float = None):
        self.object_type = object_type
        self.latitude = latitude
        self.longitude = longitude
        self.confidence = confidence

class Map(mapHelper):
    def __init__(self):
        # List will be in the form of: [{'object_type': ((lat, lon), confidence)}, {'object_type': ((lat, lon), confidence)}, etc.]
        self.map = []

    def calculate_midpoint(self, point1 : Tuple[int, int], point2: Tuple[int , int]) -> Tuple[int, int]:
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
    
    def calculate_heading_to_waypoint(self, current_point : Tuple[int, int], waypoint : Tuple[int, int]) -> float:
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
    
    def put_object_in_map(self, object : Object):
        parsed_object = {object.object_type: ((object.latitude, object.longitude), object.confidence)}
        self.map.append(parsed_object)

    def load_map_config(self, file_path : str | Path):
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
        
        def load_json(path):
            with open(path, "r") as file:
                data = json.load(file)
            return data
        
        config = load_json(file_path)

        for object_type, individual_instances in config.items():
            for index, object_specs in enumerate(individual_instances):
                latitude = object_specs["latitude"] 
                longitude = object_specs["longitude"] 
                confidence = object_specs["confidence"] 
                self.put_object_in_map(Object(object_type=object_type, latitude=latitude, longitude=longitude, confidence=confidence))
        return self.map