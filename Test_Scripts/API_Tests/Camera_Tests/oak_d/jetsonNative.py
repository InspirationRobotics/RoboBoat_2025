"""Chat GPT generated"""

import cv2
import time
import threading
import queue
from pathlib import Path
from Perception.Perception_Core.new_core import CameraCore  # Adjust path if needed
from GNC.Guidance_Core.mission_helper import MissionHelper

# Load config
config = MissionHelper().load_json(path="GNC/Guidance_Core/Config/barco_polo.json")

# Define paths to models
MODEL_1 = config["test_model_path"]
MODEL_2 = config["competition_model_path"]

# Label Map (Ensure it matches your detection classes)
LABELMAP_1 = config["test_label_map"]
LABELMAP_2 = config["competition_label_map"]

# Initialize the camera core
camera = CameraCore(model_path=MODEL_2,native=True)
camera.start()

# Function to capture frames

while True:
    start_time = time.time_ns()
    frame = camera.getFrameRaw()
    end_time = time.time_ns()
    print(f"Used {((end_time - start_time) / 1e9):.2f} s to get frame")

    cv2.imshow("rgb", frame)
    time.sleep(1 / 20)  # Adjust to match the FPS (20 FPS)