from API.Camera.oakd_poe_lr.oakd_api import OAKD_LR
from pathlib import Path
import cv2
import time
import numpy as np

# Create OAKD_LR object and start capturing frames
cam = OAKD_LR()
cam.startCapture()

while(True):
    # time.sleep(1)
    try:
        frame_rgb, depth_frame = cam.getLatestBuffers()  # Get RGB frame and depth frame
        if frame_rgb is None:
            print("No frame received")
            continue
        
        # detections = cam.getLatestDetection()  # Get object detections
        # print(detections)
          
        cv2.imshow("rgb",frame_rgb)
        cv2.imshow("depth", depth_frame)
        disp = (depth_frame * (255.0 / np.max(depth_frame))).astype(np.uint8)
        disp = cv2.applyColorMap(disp, cv2.COLORMAP_JET)
        cv2.imshow("normalized", disp)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit on pressing 'q'
            break
    except Exception as e:
        print(f"Error: {e}")

# Stop capture and release resources
cam.stopCapture()
cv2.destroyAllWindows()
