import smopy
import cv2
from GNC.Nav_Core.mapHelper import mapHelper

"""
We want to:
- Based on the map and coordinates, visualize a square-shaped map proportional to the distance between the objects

Need to load map data into the visualizer
Calculate the zoom of the map based on the coordinates
Based on the lat, lon constraints for the map, show it on the screen.
Go from there.
"""

class mapVisualizer(mapHelper):
    def __init__(self, map : list, scale : float):
        self.loaded_map = map
        self.map_scale = scale

    def parse_map_data(self):
        pass

    def calculate_map_corners(self):
        lat_min = 10000
        lat_max = 0
        lon_min = 10000
        lon_max = 0

        # Parse the map list to get the latitude and longitude.
        # List is in the form [{'object_type': ((lat, lon), confidence)}, {'object_type': ((lat, lon), confidence)}]

        for index, object in enumerate(self.loaded_map):
            for tuple in object.values():
                coordinates = tuple[0]
                latitude = coordinates[0]
                longitude = coordinates[1]

                if latitude > lat_max:
                    lat_max = latitude
                elif latitude < lat_min:
                    lat_min = latitude
                if longitude > lon_max:
                    lon_max = longitude
                elif longitude < lon_min:
                    lon_min = longitude
        
        # Make sure the map is a square.
        lat_distance = self.calculate_latitude_distance(lat_min, lat_max)
        average_latitude = self.calculate_midpoint((lat_min, lon_min), (lat_max, lon_max))[0]
        lon_distance = self.calculate_longitude_distance(lon_min, lon_max, average_latitude)

        # NOTE these calculations are not accurate since they assume cartesian points.
        if lat_distance > lon_distance:
            lon_min = lon_min - (lat_distance - lon_distance)/2
            lon_max = lon_max + (lat_distance - lon_distance)/2
        elif lon_distance > lat_distance:
            lat_min = lat_min - (lon_distance - lat_distance)/2
            lat_max = lat_max + (lon_distance - lat_distance)/2

        # Calculate the center of the square.
        southwest_corner = (lat_min, lon_min)
        northeast_corner = (lat_max, lon_max)
        center = (self.calculate_midpoint(southwest_corner, northeast_corner))
        vector_magitude = self.map_scale * self.haversine(center, southwest_corner)

        scaled_corner = self.calculate_waypoint_from_vector()


        

        

            