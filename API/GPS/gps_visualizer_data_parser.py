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

if __name__ == "__main__":
    # Change file if necessary
    file_path = Path("logs_9_15_24/motor_core1.log")
    data_parser = DataParser(file_path)
    data_parser.parse_data()
    print(data_parser.heading)