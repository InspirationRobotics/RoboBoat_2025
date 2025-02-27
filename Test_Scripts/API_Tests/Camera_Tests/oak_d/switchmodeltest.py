"""Chat GPT generated, need to modify"""
import time
from Perception.Perception_Core.perception_core import CameraCore  # Ensure this imports your CameraCore class

# Define paths to models
MODEL_1 = "Perception/Models/test_model/yolov8n_coco_640x352.blob"
MODEL_2 = "Perception/Models/test_model/yolov8n_custom_640x352.blob"

# Label Map (Ensure it matches your detection classes)
LABELMAP = [
    "person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train",
    "truck", "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench"
]

def test_switch_model():
    """Test switching between two models."""
    print("\nInitializing CameraCore with the first model...")
    camera = CameraCore(MODEL_1, LABELMAP)
    
    print("\nStarting camera...")
    camera.start()
    time.sleep(5)  # Let it run for a few seconds

    print("\nSwitching to the second model...")
    camera.switchModel(MODEL_2)
    time.sleep(5)  # Allow time for the model switch to take effect

    print("\nSwitching back to the first model...")
    camera.switchModel(MODEL_1)
    time.sleep(5)  # Ensure the camera restarts correctly

    print("\nStopping camera...")
    camera.stop()
    print("Test completed successfully!")

if __name__ == "__main__":
    test_switch_model()
