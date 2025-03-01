import json

class MissionHelper:
    def __init__(self):
        pass

    def load_json(self, path : str) -> dict:
        with open(path, "r") as file:
            config = json.load(file)
        return config
    
    def parse_config_data(self, config : dict):
        self.motor_port = config["motor_port"]
        self.gps_port = config["gps_port"]

        self.servo_port = config["mini_maestro_port"]
        self.racquetball_launcher_channel = config["racquetball_launcher_channel"]
        self.water_cannon_channel = config["racquetball_launcher_channel"]
        self.launchPWM = config["launch_PWM"]
        self.nominalPWM = config["nominal_PWM"]

        self.root_model_path = config["root_model_path"]
        self.model_path = config["test_model_path"]
        self.label_map = config["test_label_map"]

        self.waypoint_generation_method = config["waypoint_generation_method"]
        self.mission_file_location = config["mission_plan"]
        
        self.mission_sequence = self.load_json(str(self.mission_file_location))["missions"]

        if self.waypoint_generation_method == "hardcode":
            self.read_waypoints = True
            self.use_map = False
            self.waypoint_file = config["waypoint_file"]
        elif self.waypoint_generation_method == "map":
            self.read_waypoints = False
            self.use_map = True
            self.waypoint_file = None
