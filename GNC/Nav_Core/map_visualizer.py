import smopy
import cv2
import numpy as np
from GNC.Nav_Core.map_helper import mapHelper
from typing import Tuple, Union
from pathlib import Path

"""
Next Steps:
- We want to draw each individual object on the map on the map image.
- Buoys of each color will be their own color circles
- Boats will be rectangles, the same size or slightly bigger, each with their respective colors.
- Can handle difference in sizing, signs later.
"""

class mapVisualizer(mapHelper):
    def __init__(self, /, map : list = [], scale : float = 1.0, save : bool = False, zoom : int = 19, frame_size : int = 600, *,
                 path_to_save_image : str | Path):
        super().__init__()
        self.loaded_map = map
        self.map_scale = scale
        self.save = save
        self.zoom = zoom
        self.frame_size = frame_size
        
        if path_to_save_image:
            self.image_path = path_to_save_image

    def parse_map_data(self):
        pass
    
    def parse_map_corners(self) -> list:
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

        # Calculate the center of the box.
        southwest_corner = (lat_min, lon_min)
        southeast_corner = (lat_min, lon_max)
        northwest_corner = (lat_max, lon_min)
        northeast_corner = (lat_max, lon_max)

        return [southwest_corner, southeast_corner, northwest_corner, northeast_corner]
    
    def calculate_scaled_map_corners(self) -> list:
        """
        Scale the map corners to make sure all of the objects remain inside the visualized map.
        """
        corners = self.parse_map_corners()
        southwest_corner = corners[0]
        southeast_corner = corners[1]
        northwest_corner = corners[2]
        northeast_corner = corners[3]
        
        center = (self.calculate_midpoint(southwest_corner, northeast_corner))

        # Scale the map so that it extends outside of the rectangular shape created by the actual mapped objects.
        scaled_corners = [self.extend_vector(center, southwest_corner, self.map_scale), self.extend_vector(center, southeast_corner, self.map_scale),
                          self.extend_vector(center, northwest_corner, self.map_scale), self.extend_vector(center, northeast_corner, self.map_scale)
                          ]
        
        return scaled_corners
        
    def get_map(self, /, save : bool = False):
        scaled_corners = self.calculate_scaled_map_corners()
        lat_min = scaled_corners[0][0]
        lon_min = scaled_corners[0][1]
        lat_max = scaled_corners[3][0]
        lon_max = scaled_corners[3][1]
        zoom = self.zoom
        map = smopy.Map((lat_min, lon_min, lat_max, lon_max), z=zoom)
        if save:
            if not isinstance(self.image_path, Path):
                self.image_path = Path(self.image_path)
            map.save_png(f"{self.image_path}/map_visualized.png")
        self.map_obj = map
        frame = cv2.cvtColor(map.to_numpy(), cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (self.frame_size, self.frame_size), interpolation=cv2.INTER_LINEAR)
        # sharpen the frame
        frame = cv2.GaussianBlur(frame, (0, 0), 1.0)
        frame = cv2.addWeighted(frame, 1.5, frame, -0.5, 0)
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        frame = cv2.filter2D(frame, -1, kernel)
        self.frame = frame
        return map
    
    def draw(self):
        pass