from API.gps_api import GPS, GPSData

import time

def log_gps():
    log = open(f'logs/GPSlog_{int(time.time())}.txt', "w")

    def callback(data : GPSData):
        log.write(str(data) + '\n')

    gps = GPS('/dev/ttyUSB0', 115200, callback=callback)

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    del gps
    log.close()

def print_gps():

    def callback(data : GPSData):
        print(data)

    gps = GPS('/dev/ttyUSB0', 115200, callback=callback, offset=270.96788823529414)
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    del gps

if __name__ == "__main__":
    print_gps()