from pathlib import Path
import time

class Nav_Path():
    def __init__(self, *, read_waypoints : bool = False, waypoint_file : str = None, use_map : bool = False, map_file : str = None):
        self.read_waypoints = read_waypoints
        self.use_map = use_map

        if self.read_waypoints:
            self.waypoint_file = waypoint_file
            self.file = open(str(self.waypoint_file), "r")

        elif self.use_map:
            self.map_file = map_file

    def read_file(self):
        value = self.file.readline().strip()
        if value == "":
            value = None
            self.file.close()
        return value

    