"""
File to run in order to begin Barco Polo's mission. 
"""
"""
Mission:

- Go forward for 10 meters. While doing so, simulate the detections of a black and orange boat.
- Move towards the black boat and orange boat (black first).
- Fire the racquetball launcher at the black boat, water cannon at the orange boat.
- The mission should time out in 300 seconds.

TODO: BEFORE running, make sure to change DummyPerceptionThread's simulated coordinates.
"""


import time
import threading
from GNC.Control_Core import motor_core
from API.Servos import mini_maestro
from GNC.Nav_Core import map, nav_path
from GNC.Guidance_Core.mission_helper import MissionHelper
# from Perception.Perception_Core import perception_core

class DummyPerceptionThread:
    """
    Thread to simulate the detections for an orange and black boat. Basic structure for later conversion into perception thread.
    After x number of seconds, the thread will simulate the detection of a boat, and put it in the Map.map attribute (list).
    """
    def __init__(self, M):
        self.object = map.Object()
        self.map = M
        self.thread = threading.Thread(target=self.time)
        self.thread.daemon = True  # Ensures thread stops when the main program exits

        self.black = False
        self.orange = False
        self.start_time = time.time()

        self.thread.start()
    
    def time(self):
        while True:
            if self.black == True:
                self
            
            # Can add as many boats as we want with different lat and lons. 
            if time.time() - self.start_time > 10 and self.black == False:
                self.black = True
                self.object.object_type = "black_boat"
                self.object.latitude = 32.001010
                self.object.longitude = -107.101
                self.object.confidence = 100
                self.map.change_map(self.object)
            if time.time() - self.start_time > 25  and self.orange == False:
                self.orange = True
                self.object.object_type = "orange_boat"
                self.object.latitude = 32.001015
                self.object.longitude = -107.1015
                self.object.confidence = 100
                self.map.change_map(self.object)
            # if self.black == True and self.orange == True:
            #     break

            time.sleep(0.5)

    def exit(self):
        self.thread.join()

class Mission(MissionHelper):
    def __init__(self, *, config : str = "GNC/Guidance_Core/Config/barco_polo.json"):
        data = self.load_json(config)
        self.parse_config_data(data)

        self.motors = motor_core.MotorCore(self.motor_port, self.gps_port)
        self.servo = mini_maestro.MiniMaestro(self.servo_port)
        self.map = map.Map()
        self.mission_path = nav_path.Nav_Path(read_waypoints=self.read_waypoints, waypoint_file=self.waypoint_file, 
                                              use_map=self.use_map)
        self.perception_thread = DummyPerceptionThread(self.map)
        
        self.initiate_next_waypoint = False
        self.next_waypoint = None
        self.target = None
        self.end = False

        print("[MISSION] Initalizing threads...")
        time.sleep(3)

        self.motors.main(duration=300)
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
                if self.state == "waypoint":
                    # Here we are just going to move 10 meters forward. Once we have moved 10 meters forward, we are going to switch 
                    # to self.state == "rescue_deliveries".
                    self.motors.cartesian_vector_navigation(x=0, y=10)
                    self.next_waypoint = self.motors.desired_position

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
                # If black, fire racquetballs. 
                if self.target == "black_boat":
                    self.servo.set_pwm(self.racquetball_launcher_channel, self.launchPWM)
                    time.sleep(2)
                    self.servo.set_pwm(self.racquetball_launcher_channel, self.nominalPWM)
                # If orange, fire water cannon.
                elif self.target == "orange_boat":
                    self.servo.set_pwm(self.water_cannon_channel, self.launchPWM)
                    time.sleep(2)
                    self.servo.set_pwm(self.water_cannon_channel, self.nominalPWM)

                self.target = None
                self.initiate_next_waypoint = True
            else:
                self.end = True

            time.sleep(0.2)
        self.exit_mission()

    def exit_mission(self):
        self.motors.exit()
        self.mission_path.exit()
        self.servo.close()

if __name__ == "__main__":
    from GNC.Guidance_Core import old_mission

    m = old_mission.Mission()

    try:
        m.run()
    except KeyboardInterrupt:
        pass