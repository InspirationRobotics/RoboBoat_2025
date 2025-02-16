"""
Simple test script for sensor fusion. This test is considered successful if:
1. Accurate latitude and longitude data is printed out rapidly in terminal.
2. Accurate heading data is printed out rapidly in terminal.
3. Accurate velocity data is printed out rapidly in terminal.
"""

from GNC.Control_Core.sensor_fuse import SensorFuse
import time
import numpy as np

sf = SensorFuse(use_imu=True)
while True:
    lat, lon = sf.get_position()
    heading = sf.get_heading()
    velocity = sf.get_velocity()
    print(lat, lon)
    # print(heading)
    # print(velocity)
    time.sleep(0.1)