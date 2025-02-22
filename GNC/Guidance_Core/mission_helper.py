import json

class MissionHelper:
    def __init__(self):
        pass

    def load_json(self, path : str) -> dict:
        with open(path, "r") as file:
            data = json.load(file)
        return data
    
    def parse_config_data(self, data : dict):
        self.motor_port = data["motor_port"]
        self.gps_port = data["gps_port"]
        self.waypoint_generation_method = data["waypoint_generation_method"]

        if self.waypoint_generation_method == "hardcode":
            self.read_waypoints = True
            self.use_map = False
            self.waypoint_file = data["waypoint_file"]
            self.map_file = None
        elif self.waypoint_generation_method == "map":
            self.read_waypoints = False
            self.use_map = True
            self.waypoint_file = None
            self.map_file = data["map_file"]