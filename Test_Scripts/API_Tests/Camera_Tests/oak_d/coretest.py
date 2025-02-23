import cv2
import time
from Perception.Perception_Core.perception_core import CameraCore  # Adjust path if needed
from pathlib import Path
import threading
import queue

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

# Create a queue to pass frames between threads
frame_queue = queue.Queue(maxsize=4)
on = True
lock = threading.Lock()

# Function to capture frames
def capture_frames():
    global on
    while on:
        start_time = time.time_ns()
        depth = camera.get_object_depth(scale=0.2)
        frame = camera.visualize()
        end_time = time.time_ns()
        print(f"used {((end_time-start_time)/1e9):2f} s to get frame")

        # Put the captured frame into the queue
        if frame_queue.full():
            frame_queue.get()  # Remove the oldest frame
        frame_queue.put(frame)
        time.sleep(1 / 20)  # Adjust to match the FPS (20 FPS)

# Start the capture thread
capture_thread = threading.Thread(target=capture_frames, daemon=True)
capture_thread.start()

# Main loop to display frames
while on:
    if not frame_queue.empty():
        frame = frame_queue.get()
        ss = time.time_ns()
        cv2.imshow("rgb", frame)
        ee = time.time_ns()
        print(f"used {((ee-ss)/1e9):2f} s to display")
    
    # Check for the 'q' key to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit on pressing 'q'
        break

# Stop capturing
camera.stop()

# Stop the capture thread gracefully
on = False
capture_thread.join()
cv2.destroyAllWindows()
