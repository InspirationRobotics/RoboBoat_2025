import os
import time
from typing import Any, List, Tuple
from pathlib import Path
from serial import Serial
from threading import Thread, Lock
from pynmeagps import NMEAReader, NMEAMessage


"""
https://www.qso.com.ar/datasheets/Receptores%20GNSS-GPS/NMEA_Format_v0.1.pdf
Specs : GNGGA
"""

class GPSData:
    """
    Class to handle the return of various GPS data.
    """
    def __init__(self, lat : float, lon : float, headt : float):
        self.lat = lat
        self.lon = lon
        self.heading = headt
        self.timestamp = time.time()

    def is_valid(self):
        """
        Checks to make sure data is valid by making sure there is a lat, lon, heading in the data
        """
        return self.lat and self.lon and self.heading

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Puts GPS data into a dictionary and attaches the time stamp of when the data was listed
        """
        self.__dict__[name] = value
        self.__dict__["timestamp"] = time.time()

    def __str__(self) -> str:
        """
        Returns f-string of latitude, longitude, heading
        """
        return f"Lat: {self.lat}, Lon: {self.lon}, Heading: {self.heading}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
class GPS:
    """
    Class to handle all GPS functionalitiy.

    Args:
        serialport (str): Port between GPS and Jetson
        baudrate (int): Message rate on serial connection (defaults to 115200)
        callback (func): Function to run on the GPS data when data is collected
        threaded (bool): Whether or not to create a GPS thread (defaults to True)
        offset (float): Keyword argument, whether or not to take into account any sort of offset for the GPS
    """
    def __init__(self, serialport : str, baudrate : int = 115200, callback = None, threaded : bool = True, *, offset : float = None):
        stream = Serial(serialport, baudrate, timeout=3)
        self.nmr = NMEAReader(stream)
        self.threaded = threaded
        self.callback = callback
        self.offset = offset if offset is not None else self.load_heading_offset()

        self.data : GPSData = GPSData(None, None, None)
        self.lock = Lock()

        self.active = True
        self.gps_thread = Thread(target=self.__gps_thread, daemon=True)
        if threaded:
            self.gps_thread.start()

    def __del__(self):
        if self.threaded:
            self.active = False
            self.gps_thread.join(2)

    def __update_data(self, parsed_data):
        try:
            if parsed_data.msgID == 'GGA':
                    self.data.lat = parsed_data.lat
                    self.data.lon = parsed_data.lon
            elif parsed_data.msgID == 'THS':
                    self.data.heading = (parsed_data.headt + self.offset) % 360
        except Exception as e:
            # print("Error grabbing data")
            # print(e)
            pass

    def __gps_thread(self):
        parsed_data : NMEAMessage
        while self.active:
            raw_data, parsed_data = self.nmr.read() # Blocking
            with self.lock:
                self.__update_data(parsed_data)
            if self.callback and self.data.is_valid():
                self.callback(self.data)

    def __get_single_data(self) -> GPSData:
        parsed_data : NMEAMessage
        raw_data, parsed_data = self.nmr.read() # Blocking
        self.__update_data(parsed_data)
        return self.data

    def get_data(self) -> GPSData:
        if self.threaded:
            with self.lock:
                return self.data
        else:
            return self.__get_single_data()
    
    def load_heading_offset(self):
        curr_path = Path("Test_Scripts/GPS_Tests")
        config_path = curr_path / "config"
        if not config_path.exists():
            os.mkdir(config_path)
        if not (config_path / "gps_offset.txt").exists():
            return 0 # Default offset
        with open(config_path / "gps_offset.txt", "r") as f:
            offset = float(f.read())
        return offset

    def calibrate_heading_offset(self, calib_time : int = 5):
        heading_data = []
        input("Press Enter to start calibration")
        print("Calibrating GPS heading offset...")
        start_time = time.time()
        while time.time() - start_time < calib_time:
            data = self.get_data()
            if data.is_valid():
                heading_data.append(data.heading)
            time.sleep(0.3)
        avg_heading = sum(heading_data) / len(heading_data)
        print(f"Average heading: {avg_heading}")
        current_heading = input("Enter current heading: ")
        offset = float(current_heading) - avg_heading
        print(f"Offset: {offset}")
        data = input("Save offset? (y/n): ")
        if data.lower() == "y":
            curr_path = Path("Test_Scripts/GPS_Tests")
            config_path = curr_path / "config"
            if not config_path.exists():
                os.mkdir(config_path)
            with open(config_path / "gps_offset.txt", "w") as f:
                f.write(str(offset))
                print("Offset saved.")
        print("Calibration complete.")
        
    def save_waypoints(self):
        if not self.gps_thread.is_alive():
            print("GPS thread is required to save waypoints")
            return
        if self.callback is not None:
            print("GPS cannot have a callback set to save waypoints")
            return
        name = input("Enter the name for the file: ")
        auto = True if input("Auto log waypoints at 2hz? (y/n)").lower() == "y" else False
        input("Press any key to begin logging waypoints")
        curr_path = Path("Test_Scripts/GPS_Tests")
        missions_path = curr_path / "missions"
        if not missions_path.exists():
            os.mkdir(missions_path)
        log = open(f'{missions_path}/{name}.txt', "w")

        def auto_callback(data : GPSData):
            log.write(f"{data.lat} % {data.lon} % {data.heading}\n")

        with self.lock:
            self.callback = auto_callback if auto else None
        cnt = 1
        while True:
            try:
                if not auto:
                    key = input("Press any key to save a waypoint (or q to quit)")
                    if key.lower() == "q":
                        break
                    data = self.get_data()
                    log.write(f"{data.lat} % {data.lon} % {data.heading}\n")
                    print(f"Waypoint {cnt} saved")
                    cnt+=1
                else:
                    time.sleep(1)
            except KeyboardInterrupt:
                break
        print(f"Waypoints saved to {name}.txt")
        log.close()

    @staticmethod
    def load_waypoints(filename : str) -> List[Tuple[float, float]]: 
        '''
        Returns a list of waypoints in the form of a list of tuples (lat, lon)
        '''
        if filename is None:
            return None
        curr_path = Path("Test_Scripts/GPS_Tests")
        missions_path = curr_path / "missions"
        if not missions_path.exists():
            os.mkdir(missions_path)
        file_path = missions_path / filename
        if not file_path.exists():
            print(f"File {filename} does not exist")
            return None
        waypoints = []
        with open(file_path, "r") as f:
            for line in f:
                try:
                    lat, lon, heading = line.split(" % ")
                    waypoints.append((float(lat), float(lon))) #ignore heading for now
                except:
                    pass
        return waypoints