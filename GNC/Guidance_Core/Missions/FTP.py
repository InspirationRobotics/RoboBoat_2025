import time
import queue

class FTP:
    def __init__(self, *, infoCore, motors):
        self.info = infoCore
        self.motors = motors

        # Threshold to look for objects.
        self.threshold = 0.8

        # Final position at the end of the path.
        self.endPosition = (None, None)
        self.end = False

    def run(self, queue):
        # Find the two closest objects that are lowest on the screen.
        # Find the midpoint of both objects(pixel values).
        # If the difference between one midpoint is greater than the other, yaw to force the values to be within equal within a certain 
        # tolerance (while always moving forward)
        # Always move forward while yawing

        while self.end == False:
            gpsData, detections = self.info.getInfo()

            # Find the lowest two detections.
            # Going down the screen will actually increase the value, so lowest will be 1.
            # Going across the screen decreases the value (xmax -> xmin).

            # Find the lowest of each type.
            # Types are "green", "red", "yellow", "cross", "triangle"
            # "bbox": (detection.xmin, detection.ymin, detection.xmax, detection.ymax)

            green_min, red_min, yellow_min, cross_min, triangle_min = (0, 0, 0, 0, 0)
            target_green, target_red, target_yellow, target_cross, target_min = (None, None, None, None, None)

            for detection in detections:
                if detection["type"] == "green_buoy":
                    if detection["bbox"][2] > green_min and detection["bbox"][2] < self.threshold:
                        green_min = detection["bbox"][2]
                        target_green = detection

                elif detection["type"] == "red_buoy" and detection["bbox"][2] < self.threshold:
                    if detection["bbox"][2] > red_min:
                        red_min = detection["bbox"][2]
                        target_red = detection

                elif detection["type"] == "yellow_buoy" and detection["bbox"][2] < self.threshold:
                    if detection["bbox"][2] > yellow_min:
                        yellow_min = detection["bbox"][2]
                        target_yellow = detection

                elif detection["type"] == "cross" and detection["bbox"][2] < self.threshold:
                    if detection["bbox"][2] > cross_min:
                        cross_min = detection["bbox"][2]
                        target_cross = detection

                elif detection["type"] == "triangle" and detection["bbox"][2] < self.threshold:
                    if detection["bbox"][2] > triangle_min:
                        triangle_min = detection["bbox"][2]
                        target_triangle = detection

            # Find the lowest two objects.
            target_list = [target_green, target_red, target_yellow, target_cross, target_triangle]
            lowest_target, lowest_target_min = (None, 0)
            second_lowest_target, second_lowest_target_min = (None, 0)

            for target in target_list:
                if target["bbox"][2] > lowest_target_min:
                    # Move the formerly lowest targets to the second lowest position.
                    second_lowest_target_min = lowest_target_min
                    second_lowest_target = lowest_target
                    lowest_target_min = target["bbox"][2]
                    lowest_target = target

            # If two targets exist
            if second_lowest_target is not None:
                lowest_target_midpoint = (lowest_target["bbox"][1] + lowest_target["bbox"][3])/2
                second_lowest_target_midpoint = (second_lowest_target["bbox"][1] + second_lowest_target["bbox"][3])/2

                # Lowest target is on right side
                if lowest_target_midpoint < second_lowest_target_midpoint:
                    left_target = lowest_target
                    right_target = second_lowest_target
                else:
                    left_target = second_lowest_target
                    right_target = lowest_target

                # Find the midpoint of the segment between the targets.
                left_midpoint = (left_target["bbox"][1] + left_target["bbox"][3])/2
                right_midpoint = (right_target["bbox"][1] + right_target["bbox"][3])/2
                object_midpoint = (left_midpoint + right_midpoint)/2

                # If the midpoint of the targets is to the right (< 0.5), yaw CW (right), else yaw CCW (left)
                if object_midpoint < 0.5:
                    self.motors.veer(0.3, 0.3)
                else:
                    self.motors.veer(0.3, -0.3)
            else:
                self.end = True # TODO: Hit the final waypoint.
                queue.put(self.endPosition)
                break
            
            time.sleep(0.1)

            # # First, split into right, left sides.
            # right_side = []
            # left_side = []
            # for detection in detections:
            #     detection_xmid = (detection["xmin"] + detection["xmax"])/2
            #     if detection_xmid < 0.5:
            #         right_side.append(detection)
            #     else:
            #         left_side.append(detection)

            # # Then, for each side, work down the list to find the two lowest detections on each side.
            # for right_detection in right_side:
            #     pass
            # for left_detection in left_side:
            #     pass

        # while(self.dis>3):# change tolerance for end point
        #     _,detections = self.info.getInfo()
        #     # SIMPLE WAY
        #     def motorControl(pos):
        #         if pos>0.5:
        #             self.motor.yaw(0.4,0.4,-0.4,-0.4)
        #         else:
        #             self.motor.yaw(0.4,0.4, 0.4, 0.4)
        #     for object in detections:
        #         if(object["label"]=="red buoy"):
        #             bbox = object["bbox"]
        #             motorControl((bbox[0]+bbox[2])/2)
        #         elif(object["label"] == "green buoy"):
        #             bbox = object["bbox"]
        #             motorControl((bbox[0]+bbox[2])/2)
        #         else:
        #             self.motor.surge(0.5,0.5,0.5,0.5)

        #     # MAP WAY
            
