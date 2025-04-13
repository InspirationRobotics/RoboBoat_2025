# importing libraries
import cv2

# Create a VideoCapture object and read from input file
#cap = cv2.VideoCapture('2025-04-13-145055.webm')    
cap = cv2.VideoCapture('/Users/parsasedighi/Documents/GitHub/RoboBoat_2025/GNC/Guidance_Core/Missions/2025-04-13-145055.webm')    

capture=cv2.VideoCapture(0) 
half_way = capture.get(cv2.CAP_PROP_FRAME_WIDTH)/2

# Check if camera opened successfully
if (cap.isOpened()== False):
    print("Error opening video file")
    
    
found_frames = 0

# Read until video is completed
while(cap.isOpened()):
    
# Capture frame-by-frame
    ret, frame = cap.read()
    if ret == True:
    # Display the resulting frame
        Gaussian = cv2.GaussianBlur(frame, (7, 7), 0) 
        gray_image_Gaussian = cv2.cvtColor(Gaussian, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray_image_Gaussian, 127, 255, cv2.THRESH_BINARY) 
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
        #print(Gaussian.get(cv2.CAP_PROP_FRAME_WIDTH))
        i = 0
        
        # list for storing names of shapes 
        for contour in contours: 
             area = cv2.contourArea(contour)
             if area > 10000:
                print('area {}'.format(area))
                print('frame {}'.format(found_frames))
                # here we are ignoring first counter because  
                # findcontour function detects whole image as shape 
                if i == 0: 
                    i = 1
                    continue
              
                # cv2.approxPloyDP() function to approximate the shape 
                approx = cv2.approxPolyDP( 
                    contour, 0.01 * cv2.arcLength(contour, True), True) 
                  
                # using drawContours() function 
                # cv2.drawContours(Gaussian, [contour], 0, (0, 0, 255), 5) 
              
                # finding center point of shape 
                M = cv2.moments(contour) 
                if M['m00'] != 0.0: 
                    x = int(M['m10']/M['m00']) 
                    y = int(M['m01']/M['m00']) 
                    
                if len(approx) == 12: 
                    found_frames = found_frames + 1
                    if found_frames > 5:
                        cv2.drawContours(Gaussian, [contour], 0, (0, 0, 255), 5) 
                        cv2.putText(Gaussian, 'Plus', (x, y), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2) 
                        if x< half_way:
                            cv2.circle(Gaussian,(x-100,y), 10, (50, 168, 82), -1)
                        elif x > half_way:
                            cv2.circle(Gaussian,(x+100,y), 10, (50, 168, 82), -1)
                        else:
                            cv2.circle(Gaussian,(x,y), 10, (50, 168, 82), -1)




        #cv2.imshow('Frame', frame)
        cv2.imshow('Frame', Gaussian)
        
    # Press Q on keyboard to exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

# Break the loop
    else:
        break

# When everything done, release
# the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()