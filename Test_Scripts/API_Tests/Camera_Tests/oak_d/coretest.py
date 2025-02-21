from Perception.Perception_Core.perception_core import Camera
import cv2
from pathlib import Path
"""
TODO fix threaidng issue
The program cannot run consistantly, most likely caused by threaidhg issue
"""


# Path to the model blob
nnPath = str((Path(__file__).parent / Path('../../../../Perception/Models/test_model/yolov8n_coco_640x352.blob')).resolve().absolute())

# Label Map for detection classes
labelMap = [
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
cam = Camera(model_path=nnPath, labelMap=labelMap)

cam.start()

while(True):
    try:
        cv2.imshow("visualization", cam.visualize())
        print(cam.getObjectDepth())
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit on pressing 'q'
            break
    except Exception as e:
        print(f"Failed to display Error: {e}")

cam.stop()