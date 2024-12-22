"""
GPS Data Parser for GPS Visualization script.
This code is currently simply copied and pasted from the RobotX-GNC Repository.
"""

from pathlib import Path
import time

class DataParser:

    def __init__(self, file_path : Path | str):
        if isinstance(file_path, str):
            file_path = Path(file_path)
        self.file_path = file_path
        self.position = {}
        self.heading = {}

    def parse_gps_data(self, data : str):
        data = data[1:-1]
        data = data.split(', ')
        data = [float(i) for i in data]
        return tuple(data)
        
    def parse_heading_data(self, data : str):
        return float(data)

    def parse_data(self):
        with open(self.file_path, 'r') as file:
            for line in file:
                line = line.strip()
                time_stamp, data = line.split('__: ', 1)
                time_stamp = int(time_stamp)
                if "(" in data:
                    self.position[time_stamp] = self.parse_gps_data(data)
                else:
                    self.heading[time_stamp] = self.parse_heading_data(data)
        return self.position, self.heading
                

class DataParser2:
    
        def __init__(self, file_path : Path | str):
            if isinstance(file_path, str):
                file_path = Path(file_path)
            self.file_path = file_path
            self.position = {}
            self.heading = {}
            self.target = {}

        def convert_time(self, time_stamp : str):
            time_stamp = time_stamp.replace(',', '.')
            time_stamp = time_stamp.split(' ')
            date = time_stamp[0].split('-')
            _time = time_stamp[1].split(':')
            _time = [int(float(i)) for i in _time]
            date = [int(i) for i in date]
            time_stamp = time.mktime((date[0], date[1], date[2], _time[0], _time[1], _time[2], 0, 0, 0))
            return time_stamp
    
        def parse_position_data(self, data : str):
            data = data.split('Current Position: (', 1)[1]
            data = data[:-1]
            data = data.split(', ')
            data = [float(i) for i in data]
            return tuple(data)

        def parse_target_data(self, data : str):
            try:
                data = data.split('Target Position: [', 1)[1]
            except:
                data = data.split('Target Position: (', 1)[1]
            data = data[:-1]
            data = data.split(', ')
            data = [float(i) for i in data]
            return tuple(data)
            
        def parse_heading_data(self, data : str):
            data = data.split('Current: ', 1)[1]
            data = data.split(' Target: ', 1)
            current = float(data[0])
            target = float(data[1])
            return current #, target
    
        def parse_data(self):
            # Valid lines:
            # 2024-09-08 19:11:18,634 - MotorCore - DEBUG - Current Position: (32.9146337537, -117.1004477165)
            # 2024-09-08 19:11:18,636 - MotorCore - DEBUG - Target Position: [32.91426471087947, -117.10186806192723]
            # 2024-09-08 19:11:18,638 - MotorCore - DEBUG - Current: 55.147500000000036 Target: 252.80270585269335
            with open(self.file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    try:
                        time_stamp, data = line.split(' - MotorCore - DEBUG - ', 1)
                    except:
                        continue
                    time_stamp = self.convert_time(time_stamp)
                    if "Current Position" in data:
                        self.position[time_stamp] = self.parse_position_data(data)
                    elif "Target Position" in data:
                        self.target[time_stamp] = self.parse_target_data(data)
                    elif "Current" in data:
                        self.heading[time_stamp] = self.parse_heading_data(data)
            return self.position, self.target, self.heading

if __name__ == "__main__":
    file_path = Path("logs_9_15_24/motor_core1.log")
    data_parser = DataParser2(file_path)
    data_parser.parse_data()
    print(data_parser.heading)
    #print(data_parser.heading)