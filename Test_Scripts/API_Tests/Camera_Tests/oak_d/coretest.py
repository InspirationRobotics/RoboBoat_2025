import cv2
import time
from Perception.Perception_Core.perception_core import CameraCore  # Adjust path if needed
from pathlib import Path
import threading

MODEL_PATH = str((Path(__file__).parent / Path('../../../../Perception/Models/test_model/yolov8n_coco_640x352.blob')).resolve().absolute())

# Label Map for detection classes
LABELS = [
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

# Initialize the camera core
camera = CameraCore(model_path=MODEL_PATH, labelMap=LABELS)

# Start capturing
camera.start()

on = True
lock = threading.Lock()

def count():
    global on  # Explicitly declare 'on' as a global variable
    for i in range(15):
        print(f"{i} s passed")
        time.sleep(1)
    print("finishing program")
    with lock:
        on = False  # Update the global 'on' variable

countThread = threading.Thread(target=count)
countThread.start()  # Start the count thread

while(on):
    depth = camera.get_object_depth(scale=0.2)
    frame = camera.visualize()
    cv2.imshow("rgb", frame)
    # print(depth)
    # print("\n")
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit on pressing 'q'
        break

# Stop capturing
camera.stop()
countThread.join()  # Ensure the count thread finishes before the program ends
