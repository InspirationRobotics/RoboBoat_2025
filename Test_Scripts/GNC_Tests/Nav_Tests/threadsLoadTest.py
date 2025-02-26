"""
This script starts GPS and Camera background thread and put CPU usage and response time into cpu_usage_log.cvs
"""
from GNC.Nav_Core.info_core import infoCore
import time
import psutil
import csv

# Log file
LOG_FILE = "cpu_usage_log.csv"

LABELMAP = [
        "person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train",
        "truck", "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
        "bird", "cat", "dog", "horse", "sheep", "cow", "elephant",
        "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie",
        "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
        "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
        "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich",
        "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake",
        "chair", "sofa", "pottedplant", "bed", "diningtable", "toilet", "tvmonitor",
        "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", "oven",
        "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
        "teddy bear", "hair drier", "toothbrush"
    ]
# Initialize info Core
infocore = infoCore("Perception/Models/test_model/yolov8n_coco_640x352.blob",LABELMAP)
infocore.start_collecting()  # Starts background threads

# Logging results
results = {"GPS": 0, "Camera": 0, "lat":0.0,"lon":0.0,"heading":0.0,"detection":[]}

# Logging results
with open(LOG_FILE, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "CPU Usage (%)", "GPS Response Time (ms)", "Camera Response Time (ms)", "lat", "lon", "heading", "detection"])

    try:
        while True:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            cpu_usage = psutil.cpu_percent(interval=0)  # Instant CPU reading

            # Measure Camera getter response time
            start = time.time_ns()
            detect = infocore.getDetection()  # List of detected objects
            end = time.time_ns()
            results["Camera"] = (end - start) / 1e6  # Convert to milliseconds

            # Measure GPS getter response time
            start = time.time_ns()
            gpsdata = infocore.getGPSData()
            end = time.time_ns()
            results["GPS"] = (end - start) / 1e6  # Convert to milliseconds

            # Extract GPS data
            lat, lon, heading = gpsdata.lat, gpsdata.lon, gpsdata.heading

            # Convert detection list to a string
            detection_str = ";".join(detect) if detect else "None"

            # Write to CSV
            writer.writerow([timestamp, cpu_usage, results["GPS"], results["Camera"], lat, lon, heading, detection_str])

            print(f"{timestamp} | CPU: {cpu_usage}% | GPS: {results['GPS']}ms | Camera: {results['Camera']}ms")
            print(detect) if len(detect)>0 else None
            print(lat, lon, heading)
            time.sleep(1)  # Log every second

    except KeyboardInterrupt:
        print("Logging stopped.")

