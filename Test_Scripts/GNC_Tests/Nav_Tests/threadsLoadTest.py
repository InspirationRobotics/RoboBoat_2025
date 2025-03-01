"""
This script starts GPS and Camera background thread and put CPU usage and response time into cpu_usage_log.cvs
"""
from GNC.Nav_Core.info_core import infoCore
import time
import psutil
import csv
from GNC.Guidance_Core.mission_helper import MissionHelper

# Log file
LOG_FILE = "cpu_usage_log.csv"


# Load config
config = MissionHelper().load_json(path="GNC/Guidance_Core/Config/barco_polo.json")

# Define paths to models
MODEL_1 = config["test_model_path"]
MODEL_2 = config["sign_model_path"]

# Label Map (Ensure it matches your detection classes)
LABELMAP_1 = config["test_label_map"]
LABELMAP_2 = config["sign_label_map"]

# Initialize info Core
infocore = infoCore(MODEL_1,LABELMAP_1)
infocore.start_collecting()  # Starts background threads

# Logging results
results = {"response time": 0, "lat":0.0,"lon":0.0,"heading":0.0,"detection":[]}

# Logging results
with open(LOG_FILE, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "CPU Usage (%)", "Response Time (ms)", "lat", "lon", "heading"])

    try:
        while True:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            cpu_usage = psutil.cpu_percent(interval=0)  # Instant CPU reading

            # Measure Camera getter response time
            start = time.time_ns()
            gpsdata , detect = infocore.getInfo()
            end = time.time_ns()
            results["response time"] = (end - start) / 1e6  # Convert to milliseconds

            # Extract GPS data
            lat, lon, heading = gpsdata.lat, gpsdata.lon, gpsdata.heading
            

            # Write to CSV
            writer.writerow([timestamp, cpu_usage, results["response time"], lat, lon, heading])

            print(f"{timestamp} | CPU: {cpu_usage}% | response time: {results['response time']}ms")
            print(detect) if len(detect)>0 else None
            print(lat, lon, heading)
            print("\n")
            time.sleep(1)  # Log every second

    except KeyboardInterrupt:
        print("Logging stopped.")

