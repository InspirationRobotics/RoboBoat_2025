import time
from GNC.Control_Core import motor_core
from API.Servos import mini_maestro
from GNC.Nav_Core import map, nav_path
from GNC.Guidance_Core.mission_helper import MissionHelper
from Perception.Perception_Core import perception_core

class Mission(MissionHelper):
    def __init__(self, *, config : str = "GNC/Guidance_Core/Config/barco_polo.json"):
        data = self.load_json(config)
        self.parse_config_data(data)

        self.motors = motor_core.MotorCore(self.motor_port, self.gps_port)
        self.servo = mini_maestro.MiniMaestro(self.servo_port)
        self.map = map.Map()
        self.mission_path = nav_path.Nav_Path(read_waypoints=self.read_waypoints, waypoint_file=self.waypoint_file, 
                                              use_map=self.use_map)
        
        self.initiate_next_waypoint = False
        self.next_waypoint = None
        self.target = None
        self.end = False

        print("[MISSION] Initalizing threads...")
        time.sleep(3)

        self.motors.main(duration=60)
        self.state = self.mission_sequence[0]

    def run(self):
        while True:
            if self.end == True:
                break

            # If we have reached the desired waypoint, move to the next one.
            if self.initiate_next_waypoint == True:
                self.motors.desired_position = self.next_waypoint
                print(f"[MISSION] New Waypoint: {self.next_waypoint}. Target: {self.target}")
                self.next_waypoint = None
                self.initiate_next_waypoint = False

            # Logic block to find the next waypoint. Only does so when there is not a next waypoint (when we just switched to a new desired waypoint).
            # If by the end of this conditional self.next_waypoint is still None, this means there is no waypoint left in the program.
            if self.next_waypoint == None:
                if self.state == "rescue_deliveries":
                    black_boats = self.map.find_object("black_boat")
                    orange_boats = self.map.find_object("orange_boat")
                    parsed_data = {"black_boats" : black_boats, "orange_boats" : orange_boats}

                    self.command = self.mission_path.get_next_data(state=self.state, data=parsed_data)
                    self.next_waypoint = self.command["waypoint"]
                    self.target = self.command["boat_type"]


            if self.motors.target_reached == True and self.next_waypoint is not None:
                self.initiate_next_waypoint = True

            # If we are ready to fire the racquetball launcher/water cannon.
            if self.motors.target_reached == True and self.target is not None:
                # TODO: Change PWM values and barco_polo.json settings as soon as hardware setup is known.
                # If black, fire racquetballs. 
                if self.target == "black_boat":
                    self.servo.set_pwm(self.racquetball_launcher_channel, 1500)
                    time.sleep(2)
                    self.servo.set_pwm(self.racquetball_launcher_channel, 1000)
                # If orange, fire water cannon.
                elif self.target == "orange_boat":
                    self.servo.set_pwm(self.water_cannon_channel, 1500)
                    time.sleep(2)
                    self.servo.set_pwm(self.water_cannon_channel, 1000)

                self.target = None
                self.initiate_next_waypoint = True
            else:
                self.end = True

            time.sleep(0.2)
        self.exit_mission()

    def exit_mission(self):
        self.motors.exit()
        self.mission_path.exit()

if __name__ == "__main__":
    from GNC.Guidance_Core import mission
    m = mission.Mission()
    
    try:
        m.run()
    except KeyboardInterrupt:
        pass