"""For rescue delivery"""
from GNC.Nav_Core.info_core import infoCore
from GNC.Guidance_Core.waypointNav import waypointNav
from GNC.Control_Core.motor_core_new import MotorCore
from GNC.Guidance_Core.mission_helper import MissionHelper
from API.Servos import mini_maestro
import time
import math

class Rescue(MissionHelper):
    def __init__(self):
        # Init config
        self.config = self.load_json(path="GNC/Guidance_Core/Config/barco_polo.json")
        self.parse_config_data(self.config)

        self.info       = infoCore(modelPath=self.config["test_model_path"],labelMap=self.config["test_label_map"])
        self.motor      = MotorCore()
        self.wayPNav    = waypointNav()
        self.servo      = mini_maestro.MiniMaestro(self.servo_port)

        self.cross      = False
        self.triangle   = False

        self.crossObject    = []
        self.triangleObject = []

        self.objectDetected = False
        self.duration = 20
        self.startTime = time.time()

        # # Maybe? declare mini maestro channel for water gun and racketball launcher also the PWM value
        # self.racquetball_launcher_channel   = 0
        # self.water_cannon_channel           = 0
        # self.launchPWM                      = 1600
        # self.nominalPWM                     = 1800

    def start(self):
        # NOTE: Resolved -- TODO Here is a conflict, because we initialize info core in wayPNav object start method
        # Solution: put everything in a big ass file never stop wayPNav until return, pass in info core to wayPNav ...
        self.wayPNav.start()  
        # self.info.start_collecting()

    def run(self):
        on = True
        while(on):
            gps, detections = self.info.getInfo()
            for object in detections:
                label = object["label"]
                self.objectDetected = True
                if(label=="cross" or label=="black boat"):
                    self.wayPNav.loadWaypoints([object["location"]])
                    self.wayPNav.run()
                    
                    # code for water gun and racketball
                    self.servo.set_pwm(self.racquetball_launcher_channel, self.launchPWM)
                    time.sleep(2)
                    self.servo.set_pwm(self.racquetball_launcher_channel, self.nominalPWM)
                    # self.cross = True

                elif(label=="triangle"or label== "orange boat"):
                    self.wayPNav.loadWaypoints([object["location"]])
                    self.wayPNav.run()

                    # code for water gun and racketball
                    self.servo.set_pwm(self.water_cannon_channel, self.launchPWM)
                    time.sleep(2)
                    self.servo.set_pwm(self.water_cannon_channel, self.nominalPWM)

                    # self.triangle = True

            if(self.objectDetected == False and self.duration > (time.time() - self.startTime)):
                self.motor.rotate(0.2) # rotate to find target
            else: 
                on = False # stop the while loop

            
            time.sleep(0.05) # sampling rate

        print("[RESCUE DELIVERIES] Mission finished.")

    def stop(self):
        self.info.stop_collecting()
        self.wayPNav.stop()