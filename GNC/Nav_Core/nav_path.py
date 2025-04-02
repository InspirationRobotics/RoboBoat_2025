import time
from typing import Tuple

class MissionLogic:
    def __init__(self):
        pass

    def rescue_deliveries(self, data):
        # Data will be in form of {"orange_boats" : [Object, Object, Object, etc.], "black_boats" : [Object, Object, Object, etc.]}
        # Simple logic is working our way backwards from last object in list to first object in list, since we will complete Rescue 
        # Deliveries last and will want to go to the closest boat. If there are the same number of boats, we go for the black boat first (arbitrary).
        orange_boats = data["orange_boats"]
        black_boats = data["black_boats"]
        if len(orange_boats) == 0 or len(orange_boats) < len(black_boats):
            desired_object = black_boats.pop()
        elif len(black_boats) == 0 or len(black_boats) < len(orange_boats):
            desired_object = orange_boats.pop()

        # NOTE: This is temporary. Will have to come up with some other smarter method for when the lists are the same length.
        elif len(orange_boats) == len(black_boats):
            desired_object = black_boats.pop()

        waypoint = (desired_object.latitude, desired_object.longitude)
        return {"waypoint" : waypoint, "boat_type" : desired_object.type}

class Nav_Path(MissionLogic):
    def __init__(self, *, read_waypoints : bool = False, waypoint_file : str = None, use_map : bool = False):
        self.read_waypoints = read_waypoints
        self.use_map = use_map

        if self.read_waypoints:
            self.waypoint_file = waypoint_file
            self.file = open(str(self.waypoint_file), "r")

    def read_file(self):
        value = self.file.readline().strip()
        if value == "":
            value = None
            self.file.close()
        return value
    
    def calculate_data(self, state : str, data) -> dict[Tuple]:
        if state == None or data == None:
            return None
        elif state == "rescue_deliveries":
            command = self.rescue_deliveries(data)

        return command

    def get_next_data(self, *, state : str = None, data = None) -> dict[Tuple]:
        """
        Get the next data based on the given map/state. Will be a flexible dictionary, where the first position 
        is always the next waypoint (lat, lon).
        """
        if self.read_waypoints:
            waypoint = self.read_file()
            command = {"waypoint" : waypoint}
        elif self.use_map:
            command = self.calculate_data(state, data)

        return command
    
    def exit(self):
        if self.read_waypoints:
            self.file.close()

        print("[NAV PATH] Exited.")