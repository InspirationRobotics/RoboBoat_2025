"""
The data will be in the form of
"{rounded_time} % {data.lat} % {data.lon} % {data.heading}\n"
"""

from pathlib import Path

class GPSDataParser:
    def __init__(self, file_path : Path | str):
        if isinstance(file_path, str):
            file_path = Path(file_path)
        self.file_path = file_path
        self.position = {}
        self.heading = {}

    def parse_data(self):
        with open(self.file_path, 'r') as file:
            for line in file:
                line = line.strip()
                time_stamp, latitude, longitude, heading = line.split(" %", -1)
                time_stamp = int(time_stamp)
                self.position[time_stamp] = tuple([float(latitude), float(longitude)])
                self.heading[time_stamp] = float(heading)
        return self.position, self.heading

if __name__ == "__main__":
    file_path = Path(r'Test_Scripts/GPS_Tests/missions/GPS_Parser_Test.txt')
    data_parser = GPSDataParser(file_path)
    data_parser.parse_data()
    print(data_parser.position, data_parser.heading)