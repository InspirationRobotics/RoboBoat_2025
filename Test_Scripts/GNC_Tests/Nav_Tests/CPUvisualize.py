"""
This script visualize cpu usage from cpu_usage_log.csv
"""

import pandas as pd
import matplotlib
matplotlib.use("TkAgg")  # Or "Qt5Agg" if you have PyQt installed
import matplotlib.pyplot as plt


# Load the CSV file
LOG_FILE = "cpu_usage_log.csv"
df = pd.read_csv(LOG_FILE)

# Convert timestamp to datetime format
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# Plot CPU Usage
plt.figure(figsize=(12, 5))
plt.plot(df["Timestamp"], df["CPU Usage (%)"], label="CPU Usage (%)", color="blue", linestyle="-", marker="o")
plt.xlabel("Time")
plt.ylabel("CPU Usage (%)")
plt.title("CPU Usage Over Time")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.show()

# Plot Response Times for GPS and Camera
plt.figure(figsize=(12, 5))
plt.plot(df["Timestamp"], df["GPS Response Time (ms)"], label="GPS Response Time (ms)", color="red", linestyle="--", marker="s")
plt.plot(df["Timestamp"], df["Camera Response Time (ms)"], label="Camera Response Time (ms)", color="green", linestyle="--", marker="d")
plt.xlabel("Time")
plt.ylabel("Response Time (ms)")
plt.title("GPS & Camera Response Times Over Time")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.show()
