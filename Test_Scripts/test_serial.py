"""
Test in order to verify that we can send serial connections to the Arduino on Barco Polo.

This serves the dual purpose of testing port connectivity and verifying that the file on our arduino, motor_interface.ino, both work properly.
"""

import serial
import time

connection = serial.Serial(port = "/dev/ttyACM0", baudrate = 9600, timeout = 0.1)
time.sleep(1)

print("Starting test.")

command = "1500,1500,1500,1500\n"
connection.write(command.encode())

print("First command complete (neutral commands).")
time.sleep(1)

command = "1575,1500,1500,1500\n"
connection.write(command.encode())

print("Second command complete (stern port).")
time.sleep(1)

command = "1500,1575,1500,1500\n"
connection.write(command.encode())

print("Third command complete (stern starboard).")
time.sleep(1)

command = "1500,1500,1575,1500\n"
connection.write(command.encode())

print("Fourth command complete (aft port).")
time.sleep(1)

command = "1500,1500,1500,1575\n"
connection.write(command.encode())

print("Fifth command complete (aft port).")
time.sleep(1)

command = "1500,1500,1500,1500\n"
connection.write(command.encode())

print("Going back to neutral, last command complete.")
time.sleep(1)

connection.close()