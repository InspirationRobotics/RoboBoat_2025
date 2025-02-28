"""For rescue delivery"""
from GNC.Nav_Core.info_core import infoCore
from GNC.Guidance_Core.waypointNav import waypointNav
from GNC.Control_Core.motor_core_new import MotorCore
from GNC.Guidance_Core.mission_helper import MissionHelper
from API.Servos import mini_maestro
import time
import math

class Rescue:
    def __init__(self):
        self.config     = MissionHelper().load_json(path="GNC/Guidance_Core/Config/barco_polo.json")
        self.info       = infoCore(modelPath=self.config["test_model_path"],labelMap=self.config["test_label_map"])
        self.motor      = MotorCore()
        self.wayPNav    = waypointNav()
        self.servo      = mini_maestro.MiniMaestro(self.servo_port)

        self.cross      = False
        self.triangle   = False

        self.crossObject    = []
        self.triangleObject = []

        # TODO declare mini maestro channel for water gun and racketball launcher also the PWM value

    def start(self):
        self.info.start_collecting()

    
    def run(self):
        on = True
        while(on):
            gps, detections = self.info.getInfo()
            for object in detections:
                label = object["label"]
                if(label=="cross" or label=="black boat" and not self.cross):
                    self.wayPNav.loadWaypoints([object["location"]])
                    self.wayPNav.run()
                    
                    # code for water gun and racketball
                    self.servo.set_pwm(self.racquetball_launcher_channel, self.launchPWM)
                    time.sleep(2)
                    self.servo.set_pwm(self.racquetball_launcher_channel, self.nominalPWM)
                    self.cross = True

                elif(label=="triangle"or label== "orange boat" and not self.triangle):
                    self.wayPNav.loadWaypoints([object["location"]])
                    self.wayPNav.run()

                    # code for water gun and racketball
                    self.servo.set_pwm(self.water_cannon_channel, self.launchPWM)
                    time.sleep(2)
                    self.servo.set_pwm(self.water_cannon_channel, self.nominalPWM)

                    self.triangle = True
                
                    on = False # stop the while loop

            self.motor.rotate(0.2) # rotate to find target

        print("mission finished")