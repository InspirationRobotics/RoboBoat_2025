"""
This script starts GPS and Camera background thread and put CPU usage and response time into cpu_usage_log.cvs
"""
from GNC.Nav_Core.info_core import infoCore
import time
import psutil
import csv

# Log file
LOG_FILE = "cpu_usage_log.csv"

# Initialize info Core
infocore = infoCore()
infocore.start_collecting()  # Starts background threads

# Logging results
results = {"GPS": 0, "Camera": 0}

with open(LOG_FILE, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "CPU Usage (%)", "GPS Response Time (ms)", "Camera Response Time (ms)"])

    try:
        while True:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            cpu_usage = psutil.cpu_percent(interval=0)  # Instant CPU reading

            # Measure Camera getter response time
            start = time.time_ns()
            infocore.getDetection()
            end = time.time_ns()
            results["Camera"] = (end - start) / 1e6  # Convert to milliseconds

            # Measure GPS getter response time
            start = time.time_ns()
            infocore.getGPSData()
            end = time.time_ns()
            results["GPS"] = (end - start) / 1e6  # Convert to milliseconds

            # Write to CSV
            writer.writerow([timestamp, cpu_usage, results["GPS"], results["Camera"]])

            print(f"{timestamp} | CPU: {cpu_usage}% | GPS: {results['GPS']}ms | Camera: {results['Camera']}ms")

            time.sleep(1)  # Log every second

    except KeyboardInterrupt:
        """Ctrl + C to stop"""
        print("Logging stopped.")
