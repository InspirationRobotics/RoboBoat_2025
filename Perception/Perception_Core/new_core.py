from threading import Lock
import numpy as np
import cv2
import time
import math
from API.Camera.oakd_poe_lr.oakd_api import OAKD_LR
from ultralytics import YOLO

class CameraCore:
    def __init__(self, model_path: str = "", labelMap: list = [], native: bool = True):
        self.cam = OAKD_LR(native=True)
        self.cam_lock = Lock()
        self.labelMap = labelMap

        self.native = native
        self.native_model = YOLO(model_path)

        # Shared resources (protected by lock)
        self.rgb_frame = None
        self.depth_frame = None
        self.detections = []
        
        self.running = False
    
    def start(self):
        """Start camera streaming."""
        if self.running:
            print("Camera is already running.")
            return
        
        self.running = True
        try:
            if self._findCamera():
                self.cam.startCapture()  # Start capture directly
            else:
                print("ERROR: CAMERA NOT FOUND PLEASE CHECK CONNECTION")
                return
        except RuntimeError as e:
            print(f"ERROR Device not found {e}")
        print("Camera capture started.")
    
    def stop(self):
        """Stop camera streaming."""
        self.running = False
        self.cam.stopCapture()  # Stop capture directly
        print("Camera capture stopped.")
    
    def _findCamera(self) -> bool:
        """Check if the camera exists"""
        return not (self.cam.device is None)

    def process_frames(self):
        """Retrieve the latest RGB and depth frames."""
        if not self.running:
            print("Camera is not running.")
            return None, None

        with self.cam_lock:
            frames = self.cam.getLatestBuffers()
            if frames is not None:
                self.rgb_frame, self.depth_frame = frames
            else:
                print("Warning: No frames available from the camera.")
                self.rgb_frame, self.depth_frame = None, None

        if self.rgb_frame is None or self.depth_frame is None:
            print("Warning: Frames are not available.")
        
        balanced_frame = self._balance(self.rgb_frame)
        return self.crop_frame(balanced_frame), self.crop_frame(self.depth_frame)
    
    def crop_frame(self, frame):
        return frame[165:790, 317:1260 - 318]
    
    def get_detections(self, frame):
        """Retrieve the latest object detections."""
        return self.native_model(frame)
    
    def get_object_depth(self, scale: float = 0.5) -> list:
        """
        Calculate the depth of detected objects and return their details.
        
        Args:
            scale (float): Scale factor to define the size of the bounding box for depth calculation.
                        A smaller scale focuses on the center of the bounding box.
        
        Returns:
            list: A list of dictionaries containing the label, confidence, bounding box, and average depth of each object.
        """
        depth_data = []
        self.rgb_frame, self.depth_frame = self.cam.getLatestBuffers()
        detections = self.get_detections(frame=self.rgb_frame)

        if self.depth_frame is None or detections is None:
            return depth_data

        # Iterate through all detections
        for detection in detections:
            # Check if the detection contains any boxes (i.e., any objects were detected)
            if len(detection.boxes.xyxy) == 0:
                continue  # Skip if no boxes are detected
            
            # Get the first bounding box
            boxes = detection.boxes.xyxy[0].tolist()  # Get xmin, ymin, xmax, ymax as a list
            
            xmin, ymin, xmax, ymax = boxes

            # Normalize and calculate the bounding box
            bbox = self._frame_norm(self.rgb_frame, (xmin, ymin, xmax, ymax))

            # Calculate the center of the bounding box
            center_x = (bbox[0] + bbox[2]) // 2
            center_y = (bbox[1] + bbox[3]) // 2
            
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            bbox_center = (
                max(0, center_x - int(width * scale / 2)),
                max(0, center_y - int(height * scale / 2)),
                min(self.depth_frame.shape[1], center_x + int(width * scale / 2)),
                min(self.depth_frame.shape[0], center_y + int(height * scale / 2))
            )
            
            # Get the depth data from the region of interest (ROI)
            depth_crop = self.depth_frame[bbox_center[1]:bbox_center[3], bbox_center[0]:bbox_center[2]]
            avg_depth = np.mean(depth_crop) if depth_crop.size > 0 else 0
            avg_depth_meters = avg_depth / 1000  # Convert from mm to meters

            # Calculate the angle and distance based on the depth
            angle = ((((xmin + xmax) / 2)) - 0.5) * 82
            angle_rad = math.radians(angle)
            distance = abs(avg_depth_meters / (math.cos(angle_rad)))
            
            # Accessing the label and confidence
            # Assuming detection.names maps class index to label and detection.probs contains confidence
            class_id = detection.boxes.cls[0]  # Get the class ID of the first detected object
            label = detection.names[int(class_id)]  # Get the label for the class ID
            confidence = detection.probs[0] if hasattr(detection, 'probs') else 0.0  # Get confidence
            
            depth_data.append({
                "label": label,
                "confidence": confidence,
                "bbox": (xmin, ymin, xmax, ymax),
                "depth": avg_depth_meters,
                "distance": distance,
                "angle": angle
            })
        
        return depth_data

    def switchModel(self, modelPath: str, labelMap: str):
        """Switch to a different model dynamically."""
        if not modelPath:
            print("Error: Model path is empty.")
            return

        print(f"Switching model to: {modelPath}")

        self.stop()  # Stop camera capture
        while self.running:
            print("Waiting for camera capture to stop...")
            time.sleep(1)

        try:
            self.cam = OAKD_LR(model_path=modelPath, labelMap=labelMap)
            self.start()  # Restart capture with new model
            print("Model switched successfully.")
        except Exception as e:
            print(f"Error switching model: {e}")
            self.start()  # Restart with the previous model if switch fails

    def getFrameRaw(self):
        return self.cam.getLatestBuffers()
    
    def visualize(self):
        """Return a labeled OpenCV frame with bounding boxes and labels."""
        rgb, _ = self.process_frames()  # Use process_frames to get the latest frames
        print(rgb.shape)
        return rgb
        depth = self.get_object_depth(scale=0.5)
        if rgb is None:
            print("Error: RGB frame is not available for visualization.")
            return None
        
        color = (255, 0, 0)
        try:
            for object in depth:
                bbox = self._frame_norm(rgb, (object["bbox"][0], object["bbox"][1], object["bbox"][2], object["bbox"][3]))
                cv2.putText(rgb, object["label"], (bbox[0] + 10, bbox[1] + 20), 
                            cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
                cv2.putText(rgb, f"{int(object['confidence'] * 100)}%", (bbox[0] + 10, bbox[1] + 40),
                            cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
                cv2.putText(rgb, f"{object['depth']:.2f} meters", (bbox[0] + 10, bbox[1] + 60),
                            cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
                cv2.putText(rgb, f"{object['angle']:.2f} degrees", (bbox[0] + 10, bbox[1] + 80),
                            cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
                cv2.rectangle(rgb, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
        except Exception as e:
            print(f"Visualization Error: {e}")
        
        return rgb

    def _balance(self, frame, reference_Y_mean=244.41758007812504):
        if frame is None:
            print("Error: Frame is None!")
            return None

        if not isinstance(frame, np.ndarray):
            print(f"Error: Frame is not a numpy array! Type: {type(frame)}")
            return None

        if len(frame.shape) != 3 or frame.shape[2] != 3:
            print(f"Error: Frame shape is invalid! Expected (H, W, 3), got {frame.shape}")
            return None

        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        current_Y_mean = ycrcb[:, :, 0].mean()

        if reference_Y_mean is not None and current_Y_mean > 0:
            gamma = reference_Y_mean / current_Y_mean
            invGamma = 1.0 / gamma
            table = np.array([(i / 255.0) ** invGamma * 255 for i in range(256)]).astype("uint8")
            ycrcb[:, :, 0] = cv2.LUT(ycrcb[:, :, 0], table)

        balanced = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
        return balanced

    def _frame_norm(self, frame, bbox):
        """Normalize bounding box coordinates to match frame size."""
        try:
            norm_vals = np.full(len(bbox), frame.shape[0])
            norm_vals[::2] = frame.shape[1]
            return (np.clip(np.array(bbox), 0, 1) * norm_vals).astype(int)
        except Exception as e:
            print(f"Normalize bbox Error: {e}")
