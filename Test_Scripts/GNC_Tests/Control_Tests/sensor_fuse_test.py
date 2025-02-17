"""
Simple test script for sensor fusion. This test is considered successful if:
1. Accurate latitude and longitude data is printed out rapidly in terminal.
2. Accurate heading data is printed out rapidly in terminal.
3. [OPTIONAL]: Accurate velocity data is printed out rapidly in terminal. This will only work if the filter and IMU is enabled.
"""

from GNC.Control_Core.sensor_fuse import SensorFuse
import time
import numpy as np

sf = SensorFuse(enable_filter=False)
print("Waiting...")
time.sleep(5)
while True:
    lat, lon = sf.get_position()
    heading = sf.get_heading()
    velocity = sf.get_velocity()
    print(lat, lon)
    # print(heading)
    # print(velocity)
    time.sleep(0.1)
