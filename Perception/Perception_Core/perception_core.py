from threading import Thread, Lock
import numpy as np
import cv2
import time
import math
from API.Camera.oakd_poe_lr.oakd_api import OAKD_LR

class CameraCore:
    def __init__(self, model_path: str, labelMap: list):
        self.cam = OAKD_LR(model_path=model_path, labelMap=labelMap)
        self.cam_lock = Lock()
        self.labelMap = labelMap
        
        # Shared resources (protected by lock)
        self.rgb_frame = None
        self.depth_frame = None
        self.detections = []
        
        self.running = False
        self.capture_thread = None
    
    def start(self):
        """Start camera streaming in a separate thread."""
        if self.running:
            print("Camera is already running.")
            return
        
        self.running = True
        try:
            if(self._findCamera):
                self.cam.startCapture()
            else:
                print("ERROR: CAMERA NOT FOUND PLEASE CHECK CONNECTION")
                return
        except RuntimeError as e:
            print(f"ERROR Device not found {e}")
        self.capture_thread = Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        print("Camera capture started.")
    
    def stop(self):
        """Stop camera streaming."""
        self.running = False
        if self.capture_thread:
            self.capture_thread.join()
            self.capture_thread = None
            self.cam.stopCapture()
        print("Camera capture stopped.")
    
    def _findCamera(self) ->bool:
        """Check if the camera exist"""
        return not (self.cam.device is None)
    
    def _capture_loop(self):
        """Continuously fetch frames and detections in the background."""
        while self.running:
            with self.cam_lock:
                frames = self.cam.getLatestBuffers()
                if frames is not None:
                    self.rgb_frame, self.depth_frame = frames
                else:
                    print("Warning: No frames available from the camera.")
                    self.rgb_frame, self.depth_frame = None, None
                
                detections = self.cam.getLatestDetection()
                if detections is not None:
                    self.detections = detections
                else:
                    self.detections = []
            
            time.sleep(1 / self.cam.FPS)  # Sleep to match frame rate
    
    def get_latest_frames(self):
        """Retrieve the latest RGB and depth frames."""
        with self.cam_lock:
            if self.rgb_frame is None or self.depth_frame is None:
                print("Warning: Frames are not available.")
            return self.rgb_frame, self.depth_frame
    
    def get_latest_detections(self):
        """Retrieve the latest object detections."""
        with self.cam_lock:
            return self.detections
    
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
        self.rgb_frame, self.depth_frame = self.get_latest_frames()
        detections = self.get_latest_detections()

        if self.depth_frame is None or detections is None:
            # print("Error: Depth frame or detections are not available.")
            return depth_data

        for detection in detections:
            # Calculate bounding box coordinates
            bbox = self._frame_norm(self.rgb_frame, (detection.xmin, detection.ymin, detection.xmax, detection.ymax))
            
            # Calculate the center of the bounding box
            center_x = (bbox[0] + bbox[2]) // 2
            center_y = (bbox[1] + bbox[3]) // 2
            
            # Define a smaller bounding box for depth calculation
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            bbox_center = (
                max(0, center_x - int(width * scale / 2)),
                max(0, center_y - int(height * scale / 2)),
                min(self.depth_frame.shape[1], center_x + int(width * scale / 2)),
                min(self.depth_frame.shape[0], center_y + int(height * scale / 2))
            )
            
            # Crop the depth frame to the smaller bounding box
            depth_crop = self.depth_frame[bbox_center[1]:bbox_center[3], bbox_center[0]:bbox_center[2]]
            
            # Calculate the average depth (in mm) and convert to meters
            avg_depth = np.mean(depth_crop) if depth_crop.size > 0 else 0
            avg_depth_meters = avg_depth / 1000  # Convert mm to meters
            
            # Calculate the relative angle of the object
            # angle = (x-0.5) x HFOV     Camera specs: DFOV / HFOV / VFOV  100° / 82° / 56°
            angle = ((((detection.xmin+detection.xmax)/2))-0.5)* 82          # in degrees
            angle_rad = math.radians(angle)     # in radians

            # Convert perpendicular depth to actual distance
            distance = abs(avg_depth_meters/(math.cos(angle_rad)))
            # Append the result
            depth_data.append({
                "label": self.labelMap[detection.label],
                "confidence":detection.confidence,
                "bbox": (detection.xmin, detection.ymin, detection.xmax, detection.ymax),
                "depth": avg_depth_meters,
                "distance":distance,
                "angle":angle
            })
        
        return depth_data
    
    def switchModel(self, modelPath: str,labelMap:str):
        """Switch to a different model dynamically."""
        if not modelPath:
            print("Error: Model path is empty.")
            return

        print(f"Switching model to: {modelPath}")

        self.stop()  # Stop camera capture
        print("Wait for threads to close")
        time.sleep(5)
        try:
            # Create a new OAKD_LR instance with the new model
            self.cam = OAKD_LR(model_path=modelPath, labelMap=labelMap)
            
            # Restart capture with new model
            self.start()
            print("Model switched successfully.")
        except Exception as e:
            print(f"Error switching model: {e}")
            self.start()  # Restart with the previous model if switch fails


    def visualize(self):
        """Return a labeled OpenCV frame with bounding boxes and labels."""
        rgb, _ = self.get_latest_frames()
        depth = self.get_object_depth()
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
    
    def _frame_norm(self, frame, bbox):
        """Normalize bounding box coordinates to match frame size."""
        try:
            norm_vals = np.full(len(bbox), frame.shape[0])
            norm_vals[::2] = frame.shape[1]
            return (np.clip(np.array(bbox), 0, 1) * norm_vals).astype(int)
        except Exception as e:
            print("Normoalize bbox Error: {e}")