from GNC.Nav_Core.info_core import infoCore
import threading
import time
import psutil
import csv

# Log file
LOG_FILE = "cpu_usage_log.csv"

# Initialize info Core
infocore = infoCore()

# Function to simulate work and measure response time
def worker(task_name, results):
    while True:
        start_time = time.time()  # Start response time measurement
        infocore.getDetection()
        response_time = time.time() - start_time  # End response time measurement
        
        # Save response time
        results[task_name] = response_time

# Start worker threads
results = {"GPS": 0, "Camera": 0}
infocore.start_collecting()

# Logging CPU usage and response time over time
with open(LOG_FILE, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "CPU Usage (%)", "GPS Response Time (s)", "Camera Response Time (s)"])

    try:
        while True:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            cpu_usage = psutil.cpu_percent(interval=1)  # Get CPU usage

            # get camera data
            start = time.time_ns()
            infocore.getDetection()
            end = time.time_ns()
            results["Camera"] = end-start

            # get GPS data
            start = time.time_ns()
            infocore.getGPSData()
            end = time.time_ns()
            results["GPS"] = end-start

            # Write to CSV
            writer.writerow([timestamp, cpu_usage, results["GPS"], results["Camera"]])

            print(f"{timestamp} | CPU: {cpu_usage}% | GPS: {results['GPS']}s | Camera: {results['Camera']}s")
            
            time.sleep(1)  # Log every second

    except KeyboardInterrupt:
        print("Logging stopped.")
