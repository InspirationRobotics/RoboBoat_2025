# Source file: https://docs.arducam.com/UVC-Camera/Appilcation-Note/OpenCV-Python-GStreamer-on-windows/

import cv2
'''
apiPreference    preferred Capture API backends to use. 
Can be used to enforce a specific reader implementation 
if multiple are available: 
e.g. cv2.CAP_MSMF or cv2.CAP_DSHOW.
'''

# Use for linux.
# # open video0
# cap = cv2.VideoCapture(0, cv2.CAP_MSMF)

# Use video1 for Windows
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

# set width and height
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
# set fps
# cap.set(cv2.CAP_PROP_FPS, 30)
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()