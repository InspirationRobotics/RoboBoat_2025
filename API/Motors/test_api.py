import time
import smbus2
from threading import Thread, Lock

class ArduinoI2C:
    def __init__(self, address=8, bus_num=1):
        self.address = address
        self.bus = smbus2.SMBus(bus_num)

    def send_PWM(self, command):
        """
        Sends a list of PWM values to the Arduino via I2C.

        Args:
            command (list): List of 4 PWM values (1200 to 1800)
        """
        data = []
        for value in command:
            data.extend([value >> 8, value & 0xFF])
        
        self.bus.write_i2c_block_data(self.address, 0, data)
        print(f"Sent PWM: {command}")

class T200(ArduinoI2C):
    def __init__(self, address=8, bus_num=1, debug=False):
        super().__init__(address, bus_num)
        self.debug = debug
        self.forward_port_speed = 0
        self.forward_starboard_speed = 0
        self.aft_port_speed = 0
        self.aft_starboard_speed = 0
        self.motor_PWM_list = [1500] * 4

        self.lock = Lock()
        self.active = True
        self.send_thread = Thread(target=self.set_speed_thread, daemon=True)
        self.send_thread.start()

    def debug_decorator(func):
        def wrapper(self, *args, **kwargs):
            if self.debug:
                print("Debug mode: Skipping execution")
                return
            return func(self, *args, **kwargs)
        return wrapper

    @debug_decorator
    def set_thrusters(self, forward_port, forward_starboard, aft_port, aft_starboard):
        with self.lock:
            self.forward_port_speed = min(0.85, max(forward_port, -0.85))
            self.forward_starboard_speed = min(0.85, max(forward_starboard, -0.85))
            self.aft_port_speed = min(0.85, max(aft_port, -0.85))
            self.aft_starboard_speed = min(0.85, max(aft_starboard, -0.85))

    def set_speed_thread(self):
        while self.active:
            with self.lock:
                motor_speeds = [self.forward_port_speed, self.forward_starboard_speed, self.aft_port_speed, self.aft_starboard_speed]
                
                for index, value in enumerate(motor_speeds):
                    PWM_value = int(1500 + value * 300)
                    if PWM_value != 1500 and abs(PWM_value - 1500) <= 40:
                        PWM_value = 1460 if PWM_value < 1500 else 1540
                    self.motor_PWM_list[index] = PWM_value

            self.send_PWM(self.motor_PWM_list)
            time.sleep(1.5)

    @debug_decorator
    def stop_thrusters(self):
        self.set_thrusters(0, 0, 0, 0)
        time.sleep(5)
        self.active = False
        self.send_thread.join(2)
        print("Thrusters stopped")

    def __del__(self):
        self.stop_thrusters()
