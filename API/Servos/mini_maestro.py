import serial
import time

class MiniMaestro:
    def __init__(self, port, baudrate=9600):
        """
        Initializes the serial connection to the Mini Maestro Servo Controller.
        :param port: The COM port (e.g., "COM3" for Windows or "/dev/ttyUSB0" for Linux/Mac).
        :param baudrate: Communication speed (default is 9600).
        """
        self.serial_conn = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Allow time for the connection to establish

        # Default servo states
        self.torpedo_state = {0: (2, 1500), 1: (2, 1700), 2: (2, 1300)}
        self.dropper_state = {0: (1, 1500), 1: (1, 1200), 2: (1, 700)}
        #self.gripper_state = {0: (0, 1500), 1: (0, 1550), 2: (0, 1450)}
        #
        ## Set default positions
        self.set_pwm(*self.torpedo_state[0])
        self.set_pwm(*self.dropper_state[0])
        #self.set_pwm(*self.gripper_state[0])

    def set_pwm(self, channel, target):
        """
        Sends a command to set the PWM signal for a servo.
        :param channel: The servo channel (0-5 for Mini Maestro 6).
        :param target: PWM value (in microseconds, typically 500-2500).
        """
        target = target * 4  # Convert to Maestro format
        lsb = target & 0x7F  # Lower 7 bits
        msb = (target >> 7) & 0x7F  # Upper 7 bits
        command = bytes([0x84, channel, lsb, msb])  # Compact binary command
        self.serial_conn.write(command)

    def close(self):
        """Closes the serial connection."""
        if self.serial_conn.is_open:
            self.serial_conn.close()

# Example usage:
if __name__ == "__main__":
    # Change port based on your system (e.g., "COM3" on Windows, "/dev/ttyUSB0" on Linux/Mac)
    # maestro = MiniMaestro(port="/dev/ttyUSB0")
    maestro = MiniMaestro(port="COM5")

    # Move servos to new positions
    maestro.set_pwm(0, 1500)  # Move servo on channel 0
    time.sleep(2)
    maestro.set_pwm(0, 1600)  # Move servo on channel 0   
    time.sleep(2)
    maestro.set_pwm(0, 1800)  # Move servo on channel 0
    
    maestro.set_pwm(1, 1500)  # Move servo on channel 0
    time.sleep(2)
    maestro.set_pwm(1, 1600)  # Move servo on channel 0   
    time.sleep(2)
    maestro.set_pwm(1, 1800)  # Move servo on channel 0
    #maestro.set_pwm(1, 1200)  # Move servo on channel 1
    #maestro.set_pwm(2, 1800)  # Move servo on channel 2

    # Close connection when done
    maestro.close()