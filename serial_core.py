"""
Classes to handle sending PWM values to the Arduino via serial connection.
"""

# TODO: PWM logic, etc. (see below)

import time
import serial
from threading import Thread, Lock

class Arduino:
    def __init__(self, port="/dev/ttyACM0"):
        self.arduino = serial.Serial(port=port, baudrate = 9600, timeout = 0.1)

        self.set_pwm(self, [1500] * 4)
        time.sleep(1)
 
    def send_PWM(self, command : str):
        self.arduino.write(str(command).encode())

class T200(Arduino):
    def __init__(self, port = "/dev/tty/ACM0", debug = False):
        self.debug = debug

        if not debug:
            super().__init__(port)
            
            self.send_thread = Thread(target = self.set_speed_thread, daemon = True)
            self.lock = Lock()
            self.active = True
            
            self.send_thread.start()

    def debug_decorator(func):
        def wrapper(self, *args, **kwargs):
            if self.debug:
                return
            
            return func(self, *args, **kwargs)
        
        return wrapper
    

    # NOTE: Not sure how I want to go about this.
    # Will probably have to work on motor core first, but that will bring in a lot of sources for error.
    # Maybe just pass in an argument for each thruster (stern_port, etc.), and put that in a list, then send.
    # Will have to deal with whether thrusters will move if below a certain PWM value.
    # TODO: Logic for PWM commands, sending command. Everything below here.
    # DONE: Everything above this series of comments should be at least nominally completed.

    @debug_decorator
    def set_thrusters(self, ):
        pass

    def set_speed_thread(self):
        while self.active:
            with self.lock:
                pass