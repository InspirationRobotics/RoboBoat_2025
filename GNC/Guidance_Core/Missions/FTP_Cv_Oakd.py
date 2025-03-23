import cv2
import numpy as np

def preprocess_frame(frame):
    """ Convert to HSV and apply Gaussian Blur """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv = cv2.GaussianBlur(hsv, (5, 5), 0)
    return hsv

def get_red_mask(hsv):
    """ Create a binary mask for detecting red objects in HSV """
    # Define red color range (two parts due to HSV wrap-around)
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    # Create masks for both red ranges
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    # Combine both masks
    mask = mask2

    # Apply morphological operations to remove noise
    kernel = np.ones((5, 5), np.uint8)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask

def get_green_mask(hsv):
    """ Create a binary mask for detecting green objects in HSV """
    # Define green color range
    lower_green = np.array([70, 50, 130])   # Adjusted lower bound
    upper_green = np.array([90, 255, 255]) 

    # Create mask for the green range
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Apply morphological operations to remove noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    
    return mask

def detect_objects(frame, mask):
    """ Find contours and draw bounding boxes around detected red objects """
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:  # Filter small objects
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green box
            cv2.putText(frame, "Red Object", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.6, (0, 255, 0), 2)

    return frame

def find_extreme(mask):
    """find left and right most object"""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Initialize variables to store extreme objects
    leftmost_x = float('inf')
    rightmost_x = float('-inf')
    leftmost_contour = None
    leftmost_center = None
    rightmost_contour = None
    rightmost_center = None


    # Loop through contours to find the extreme objects
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500:  # Filter small objects
            x, y, w, h = cv2.boundingRect(contour)  # Get bounding box

            if x < leftmost_x:  # Update leftmost object
                leftmost_x = x
                leftmost_contour = contour
                leftmost_center = x + w//2

            if x + w > rightmost_x:  # Update rightmost object
                rightmost_x = x + w
                rightmost_contour = contour
                rightmost_center = x + w//2

    return leftmost_center,rightmost_center


def find_largest(mask,threshold:int = 500):
    """Find the largest contour and its centroid in the given binary mask."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None, None  # No object found

    # Find the largest contour by area
    largest_contour = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest_contour)
    if area>threshold:
        # Compute the centroid using image moments
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            center = (cx, cy)
        else:
            center = None  # Avoid division by zero
        
        return largest_contour, center
    else:
        return None, None
    
def find_lowest(mask,threshold:int = 320):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    lowest_x = 0
    lowest_y = 0
    for object in contours:
        x, y, w, h = cv2.boundingRect(object)
        if(y+h>lowest_y):
            lowest_x = x+w//2
            lowest_y = y+h
    
    return (lowest_x,lowest_y)

def draw_colored_point_on_mask(mask, center, color=(0, 0, 255)):
    """Convert mask to BGR and draw a colored point at the given center"""
    # Draw a circle at the center in the specified color
    if center:
        cv2.circle(mask, center, 5, color, -1)  # -1 to fill the circle

    return mask

class cvCore:
    def __init__(self,info):
        self.info = info  #"/home/chaser/Downloads/02_h264.mp4"
        self.lock = threading.Lock


    def control_loop_test(self):
        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            return

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            hsv = preprocess_frame(frame)
            red_mask = get_red_mask(hsv)
            green_mask = get_green_mask(hsv)

            _ ,red_buoy = find_largest(red_mask)
            _ ,green_buoy = find_largest(green_mask)

            # convert to BGR
            red_mask = cv2.cvtColor(red_mask, cv2.COLOR_GRAY2BGR)
            green_mask = cv2.cvtColor(green_mask, cv2.COLOR_GRAY2BGR)
            if red_buoy is not None:
                red_mask = draw_colored_point_on_mask(red_mask,red_buoy)
            if green_buoy is not None:
                green_mask = draw_colored_point_on_mask(green_mask,green_buoy)

            # integrate masks
            combined = red_mask + green_mask 
            # Show output
            cv2.imshow("Original", frame)
            cv2.imshow("combined", combined)

            # Press 'q' to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
    
    def control_loop(self,motor=None,debug=False):
        while True:
            _,_,frame = self.info.getInfo(visualize=True)

            hsv = preprocess_frame(frame)
            red_mask = get_red_mask(hsv)
            green_mask = get_green_mask(hsv)

            if debug:
                combined = red_mask + green_mask
                cv2.imshow("ori", frame)
                cv2.imshow("mask", combined)
                if cv2.waitKey(100) & 0xFF == ord('q'):  # Exit on pressing 'q'
                    break
    
            _ ,red_buoy = find_largest(red_mask,threshold=500)
            _ ,green_buoy = find_largest(green_mask,threshold=200)

            # red_buoy = find_lowest(red_mask)
            # green_buoy = find_lowest(green_mask)

            # normalizing
            if red_buoy is not None:
                red_buoy = red_buoy[0]/640
            if green_buoy is not None:
                green_buoy = green_buoy[0]/640

            # see both, use midpoint to navigate
            if(red_buoy is not None and green_buoy is not None):
                midpoint = (red_buoy+green_buoy)/2
                # control motor to veer(add some p control)
                
                delta_normalized = (midpoint-0.5)
                #print("[DEBUG] turn right") if delta_normalized>0 else print("[DEBUG] turn left")
                #motor.sway(delta_normalized*(0.2/0.5), 0.2)
                if delta_normalized < 0.2:
                    print(f"[DEBUG] surge")
                    motor.surge(0.2)
                else:
                    print("[DEBUG] turn left") if delta_normalized<0 else print("[DEBUG] turn right")
                    motor.sway(0.1,0.1)
            elif(red_buoy is None):
                print("[DEBUG] turn left")
                if green_buoy is not None:
                    # in 4 section
                    if green_buoy >0.5:
                        if green_buoy > 0.75:
                            motor.surge(0.2)
                        else:
                            motor.sway(-0.1,0.1)
                    else:
                        if green_buoy < 0.25:
                            motor.sway(-0.15,0.1)
                        else:
                            motor.sway(-0.2,0.1)
            elif(green_buoy is None):
                print("[DEBUG] turn right")
                if red_buoy is not None:
                    # 4 section -> turn right
                    if red_buoy > 0.5:
                        if red_buoy >0.75:
                            motor.sway(0.2,0.1)                            
                        else:
                            motor.sway(0.15,0.1)
                    else:
                        if red_buoy > 0.25:
                            motor.sway(0.1,0.1)
                        else:
                            motor.surge(0.2)

            print(f"DEBUG: redX: {red_buoy} | greenX: {green_buoy}")

            time.sleep(1/20)

if __name__ == "__main__":
    # TODO merge this repo with competition branch, import motor to pass into contorl_loop
    from GNC.Control_Core.motor_core import MotorCore
    from GNC.info_core import infoCore
    import threading
    import time
    from GNC.Guidance_Core.mission_helper import MissionHelper
    config     = MissionHelper()
    print("loading configs")
    config     = config.load_json(path="GNC/Guidance_Core/Config/barco_polo.json")
    info       = infoCore(modelPath=config["competition_model_path"],labelMap=config["competition_label_map"])
    print("start background threads")
    info.start_collecting()
    motor      = MotorCore("/dev/ttyACM2",debug=False)
    cam = cvCore(info=info)
    cam.control_loop(motor=motor,debug=False)



