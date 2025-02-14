import time
import numpy as np
from unittest import TestCase, main
from unittest.mock import patch

from GNC.Control_Core.sensor_fuse import SensorFuse
from API.GPS.gps_api import GPSData
from API.IMU.imu_api import IMUData

# TODO: Figure out how to circumvent the "unable to detect board" issue in the IMU API.

class TestSensorFuse(TestCase):
    def setUp(self):
        """Initialize the SensorFuse object with filter enabled while patching GPS and IMU classes."""
        # Patch the GPS and IMU classes to avoid hardware initialization errors.
        gps_patcher = patch('API.GPS.gps_api.GPS', autospec=True)
        self.mock_gps = gps_patcher.start()
        self.addCleanup(gps_patcher.stop)

        imu_patcher = patch('API.IMU.imu_api.IMU', autospec=True)
        self.mock_imu = imu_patcher.start()
        self.addCleanup(imu_patcher.stop)

        # Now instantiating SensorFuse will use the mocked GPS and IMU classes.
        self.sensor_fuse = SensorFuse(enable_filter=True, use_imu=True)
        self.sensor_fuse.connected = True  # Simulate a successful GPS connection.

    def test_gps_update(self):
        """Test the Kalman filter update with GPS data"""
        gps_data = GPSData(lat=37.7749, lon=-122.4194, heading=90.0)
        self.sensor_fuse._gps_callback(gps_data)
        
        position = self.sensor_fuse.get_position()
        heading = self.sensor_fuse.get_heading()
        
        self.assertIsNotNone(position)
        self.assertIsNotNone(heading)
        self.assertAlmostEqual(position[0], 37.7749, places=4)
        self.assertAlmostEqual(position[1], -122.4194, places=4)
        self.assertAlmostEqual(heading, 90.0, places=1)

    def test_imu_update(self):
        """Test the Kalman filter update with IMU data"""
        imu_data = IMUData(accel=[0.1, 0.1, 0], quat=[0, 0, 0, 1])
        self.sensor_fuse.imu_dt = time.time() - 1  # Simulate 1 second passed
        self.sensor_fuse._imu_callback(imu_data)
        
        velocity = self.sensor_fuse.get_velocity()
        self.assertIsNotNone(velocity)
        self.assertGreater(abs(velocity[0]), 0)
        self.assertGreater(abs(velocity[1]), 0)

    def test_position_estimation(self):
        """Test position estimation after multiple updates"""
        gps_data_1 = GPSData(lat=37.7749, lon=-122.4194, heading=90.0)
        gps_data_2 = GPSData(lat=37.7750, lon=-122.4193, heading=90.0)
        
        self.sensor_fuse._gps_callback(gps_data_1)
        time.sleep(1)
        self.sensor_fuse._gps_callback(gps_data_2)
        
        position = self.sensor_fuse.get_position()
        self.assertIsNotNone(position)
        self.assertAlmostEqual(position[0], 37.7750, places=4)
        self.assertAlmostEqual(position[1], -122.4193, places=4)

    def test_velocity_estimation(self):
        """Test velocity estimation after multiple updates"""
        gps_data_1 = GPSData(lat=37.7749, lon=-122.4194, heading=90.0)
        self.sensor_fuse._gps_callback(gps_data_1)
        
        time.sleep(1)
        gps_data_2 = GPSData(lat=37.7750, lon=-122.4193, heading=90.0)
        self.sensor_fuse._gps_callback(gps_data_2)
        
        velocity = self.sensor_fuse.get_velocity()
        self.assertIsNotNone(velocity)
        self.assertGreater(abs(velocity[0]), 0)
        self.assertGreater(abs(velocity[1]), 0)

if __name__ == "__main__":
    main()
