from threading import Thread, Lock
import numpy as np
import cv2
import time
import math
from API.Camera.oakd_api import OAKD_LR

class CameraCore:
    """
    This is the camera core to do some calculation base on the information get from the api
    """
    def __init__(self, model_path: str, labelMap: list):
        self.cam = OAKD_LR(model_path=model_path, labelMap=labelMap)
        self.labelMap = labelMap
    
    def start(self):
        """Start camera streaming in a separate thread."""
        self.cam.startCapture()
    
    def stop(self):
        """Stop camera streaming."""
        self.cam.stopCapture()
        print("[DEBUG] Camera capture stopped.")
    
    def _align(self):
        """align rgb frame with depth frame"""
        pass
    
    def _findCamera(self) ->bool:
        """Check if the camera exist"""
        return self.cam._findCamera()
    
    def getLatestInfo(self):
        """return rgb, depth, detection informaiton"""
        return self.cam.getLatestBuffers(), self.cam.getLatestDepth(), self.cam.getLatestDetection()
    
    def get_object_depth(self, scale: float = 0.5, visualize:bool = False) -> list:
        """
        Calculate the depth of detected objects and return their details.
        
        Args:
            scale (float): Scale factor to define the size of the bounding box for depth calculation.
                          A smaller scale focuses on the center of the bounding box.
        
        Returns:
            list: A list of dictionaries containing the label, confidence, bounding box, and average depth of each object.
        """
        depth_data = []
        rgb_frame ,depth_frame, detections = self.getLatestInfo()

        if depth_frame is None or detections is None:
            print("Error: Depth frame or detections are not available.")
            return depth_data

        for detection in detections:
            # Calculate bounding box coordinates
            bbox = self._frame_norm(rgb_frame, (detection.xmin, detection.ymin, detection.xmax, detection.ymax))
            
            # Calculate the center of the bounding box
            center_x = (bbox[0] + bbox[2]) // 2
            center_y = (bbox[1] + bbox[3]) // 2
            
            # Define a smaller bounding box for depth calculation
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            bbox_center = (
                max(0, center_x - int(width * scale / 2)),
                max(0, center_y - int(height * scale / 2)),
                min(depth_frame.shape[1], center_x + int(width * scale / 2)),
                min(depth_frame.shape[0], center_y + int(height * scale / 2))
            )
            
            # Crop the depth frame to the smaller bounding box
            depth_crop = depth_frame[bbox_center[1]:bbox_center[3], bbox_center[0]:bbox_center[2]]
            
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
            # Top left corner is xmin, ymin, lower right corner is xmax, ymax.
            depth_data.append({
                "label": self.labelMap[detection.label],
                "confidence":detection.confidence,
                "bbox": (detection.xmin, detection.ymin, detection.xmax, detection.ymax),
                "center": (int((detection.xmin+detection.xmax)/2),int((detection.ymin+detection.ymax)/2)),
                "depth": avg_depth_meters,
                "distance":distance,
                "angle":angle
            })
        
        return depth_data if not visualize else rgb_frame,depth_data
    
    def switchModel(self, modelPath: str,labelMap:str):
        """DEPRECATED"""
        """Switch to a different model dynamically."""
        if not modelPath:
            print("Error: Model path is empty.")
            return

        print(f"Switching model to: {modelPath}")

        self.stop()  # Stop camera capture
        print("[DEBUG] Wait for threads to close")
        time.sleep(5)
        try:
            # Create a new OAKD_LR instance with the new model
            self.cam = OAKD_LR(model_path=modelPath, labelMap=labelMap)
            
            # Restart capture with new model
            self.start()
            print("[DEBUG] Model switched successfully.")
        except Exception as e:
            print(f"Error switching model: {e}")
            self.start()  # Restart with the previous model if switch fails

    def visualize(self):
        """Return a labeled OpenCV frame with bounding boxes and labels."""
        rgb, detections = self.get_object_depth(scale=0.5,visualize=True)

        if rgb is None:
            print("[Error] RGB frame is not available for visualization.")
            return None
        
        color = (255, 0, 0)
        try:
            for object in detections:
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
            print(f"[Error] Visualization Error: {e}")
        
        return rgb
    
    def _balance(self, frame, reference_Y_mean=244.41758007812504):
        """DEPRECATED"""
        """
        This is a function to balance the brightness and saturation of the frame
        when having back light(facing the sun), cannot apply to oak_d preprocessing
        because of its unique pipeline.
        For more information, search up rolling average exposure
        """
        if frame is None:
            print("[Error] Frame is None!")
            return None

        # Ensure frame is a valid numpy array
        if not isinstance(frame, np.ndarray):
            print(f"[Error] Frame is not a numpy array! Type: {type(frame)}")
            return None

        # Ensure frame is 3D (H, W, 3) and not grayscale or empty
        if len(frame.shape) != 3 or frame.shape[2] != 3:
            print(f"[Error] Frame shape is invalid! Expected (H, W, 3), got {frame.shape}")
            return None

        # Convert full frame to YCrCb
        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)

        # Compute current frame brightness
        current_Y_mean = ycrcb[:, :, 0].mean()

        # Compute brightness adjustment factor
        if reference_Y_mean is not None and current_Y_mean > 0:
            gamma = reference_Y_mean / current_Y_mean  # Gamma correction factor
            invGamma = 1.0 / gamma
            table = np.array([(i / 255.0) ** invGamma * 255 for i in range(256)]).astype("uint8")
            ycrcb[:, :, 0] = cv2.LUT(ycrcb[:, :, 0], table)

        # Convert back to BGR
        balanced = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

        return balanced

    
    def _frame_norm(self, frame, bbox):
        """Normalize bounding box coordinates to match frame size."""
        try:
            norm_vals = np.full(len(bbox), frame.shape[0])
            norm_vals[::2] = frame.shape[1]
            return (np.clip(np.array(bbox), 0, 1) * norm_vals).astype(int)
        except Exception as e:
            print("[ERROR] Normoalize bbox Error: {e}")


if __name__ == "__main__":
    from GNC.Guidance_Core.mission_helper import MissionHelper
    # Load config
    config = MissionHelper().load_json(path="GNC/Guidance_Core/Config/barco_polo.json")

    # Define paths to models
    MODEL_1 = config["test_model_path"]
    MODEL_2 = config["competition_model_path"]

    # Label Map (Ensure it matches your detection classes)
    LABELMAP_1 = config["test_label_map"]
    LABELMAP_2 = config["competition_label_map"]

    cam = CameraCore(model_path=MODEL_2,labelMap=LABELMAP_2)
    cam.start()

    while(True):  
        #rgb, depth, detection = cam.getLatestInfo()

        rgb = cam.visualize()

        cv2.imshow("frame", rgb)

        if cv2.waitKey(100) & 0xFF == ord('q'):  # Exit on pressing 'q'
            break

    cv2.destroyAllWindows()