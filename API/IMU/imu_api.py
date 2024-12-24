"""
NOTE: This code has not yet been reviewed. There is no test script to verify its functionality, as well as the associated hardware setup.
"""

import time
import board
import busio

from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_LINEAR_ACCELERATION,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
    BNO_REPORT_GRAVITY
)
from adafruit_bno08x.i2c import BNO08X_I2C

import numpy as np
from pathlib import Path
from typing import Tuple, Any
from threading import Thread, Lock
from math import atan2, sqrt, pi

class IMUData:

    def __init__(self, accel : tuple = None, gyro : tuple = None, mag : tuple = None, quat : tuple = None, euler : tuple = None):
        self.accel = accel
        self.gyro = gyro
        self.mag = mag
        self.quat = quat
        self.euler = euler
        self.timestamp = time.time()
        
    @staticmethod
    def _quat_to_euler(quat : Tuple[float, float, float, float]) -> Tuple[float, float, float]:
        # This function should convert a quaternion to its euler representation
        w, x, y, z = quat
        # Roll
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = atan2(sinr_cosp, cosr_cosp)
        # Pitch
        sinp = sqrt(1 + 2 * (w * y - x * z))
        cosp = sqrt(1 - 2 * (w * y - x * z))
        pitch = 2 * atan2(sinp, cosp) - pi / 2
        # Yaw
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = atan2(siny_cosp, cosy_cosp)
        return roll, pitch, yaw
        
    def __setattr__(self, name: str, value: Any) -> None:
        self.__dict__[name] = value
        self.__dict__["timestamp"] = time.time()


class IMU:

    def __init__(self, callback = None, threaded : bool = True, calibrate = False):
        self.threaded = threaded
        self.callback = callback

        # current_path = CURRENT_FILE_PATH = Path(__file__).parent.absolute()
        # save_path = current_path / "calib/accel_offset.txt"
        # self.calibrated = False
        # if save_path.is_file():
        #     print("Found accel calibration...")
        #     self.calibrated = True
        #     self.accel_calib = np.loadtxt(save_path)

        self.bno = self.imu_init()
        self.data : IMUData = IMUData(None, None, None, None)
        
        self.lock = Lock()
        self.active = True
        self.imu_thread = Thread(target=self.__imu_thread, daemon=True)

        if threaded:
            self.imu_thread.start()

        # if calibrate:
        #     self.calib_accel_offset()

    def __del__(self):
        if self.threaded:
            self.active = False
            self.imu_thread.join(2)

    def imu_init(self):
        i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
        bno = BNO08X_I2C(i2c)
        bno.enable_feature(BNO_REPORT_LINEAR_ACCELERATION)
        bno.enable_feature(BNO_REPORT_GYROSCOPE)
        bno.enable_feature(BNO_REPORT_MAGNETOMETER)
        bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)
        bno.enable_feature(BNO_REPORT_GRAVITY)
        return bno

    def _get_single_data(self) -> IMUData:
        data = IMUData()
        accel = list(self.bno.linear_acceleration)
        for i in range(3):
            accel[i] = accel[i] if abs(accel[i]) > 0.005 else 0
        data.accel = tuple(accel) # - self.accel_calib if self.calibrated else accel
        data.gyro = self.bno.gyro
        data.mag = self.bno.magnetic
        data.quat = self.bno.quaternion
        data.euler = IMUData._quat_to_euler(data.quat)
        return data

    def __imu_thread(self):
        while self.active:
            with self.lock:
                data = self._get_single_data()
                self.data = data
            if self.callback:
                self.callback(data)
            time.sleep(0.01)

    def get_data(self):
        if not self.threaded:
            return self._get_single_data()
        with self.lock:
            return self.data
        
    # def calib_accel_offset(self, duration=5, *, save=True):
    #     # NOTE this is unideal since the calib should be on the sensor itself but oh well
    #     self.calibrated = False
    #     samples = 0
    #     avgs = np.array([0,0,0], dtype=np.float32)
    #     print(f"Calibrating accel for {duration} second(s)...")
    #     start_time = time.time()
    #     while time.time() - duration < start_time:
    #         data = self.get_data()
    #         avgs += [data.accel[0],data.accel[1],data.accel[2]]
    #         samples+=1
    #         time.sleep(0.1)
    #     calib = avgs/samples
    #     if save:
    #         current_path = CURRENT_FILE_PATH = Path(__file__).parent.absolute()
    #         save_path = current_path / "calib/accel_offset.txt"
    #         np.savetxt(save_path, calib)
    #     print(calib)
    #     self.accel_calib = calib
    #     self.calibrated = True