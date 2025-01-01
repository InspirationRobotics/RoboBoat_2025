import smopy
import cv2
from GNC.Nav_Core.map_helper import mapHelper

"""
We want to:
- Based on the map and coordinates, visualize a square-shaped map proportional to the distance between the objects

Need to load map data into the visualizer
Calculate the zoom of the map based on the coordinates
Based on the lat, lon constraints for the map, show it on the screen.
Go from there.
"""

class mapVisualizer(mapHelper):
    def __init__(self, /, map : list, scale : float):
        super().__init__()
        self.loaded_map = map
        self.map_scale = scale

    def parse_map_data(self):
        pass

    def calculate_map_corners(self) -> list:
        lat_min = 10000
        lat_max = -10000
        lon_min = 10000
        lon_max = -10000

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

        # # Calculate the center of the box.
        southwest_corner = (lat_min, lon_min)
        southeast_corner = (lat_min, lon_max)
        northwest_corner = (lat_max, lon_min)
        northeast_corner = (lat_max, lon_max)
        
        center = (self.calculate_midpoint(southwest_corner, northeast_corner))

        scaled_corners = [self.extend_vector(center, southwest_corner, self.map_scale), self.extend_vector(center, southeast_corner, self.map_scale),
                          self.extend_vector(center, northwest_corner, self.map_scale), self.extend_vector(center, northeast_corner, self.map_scale)
                          ]
        
        return (scaled_corners)   
        

        

            