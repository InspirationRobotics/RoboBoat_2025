import cv2

# create video capture object for camera 
# 0 means the first camera
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

# find all necessary configs
class cam:
    width: int = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height: int = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps: float = cap.get(cv2.CAP_PROP_FPS)
    size:tuple = (width,height)

# create a video writer
# params: name:str, output type, fps:float, (width:int,height:int)
out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), cam.fps, cam.size)

while(True):

    # Capture frame-by-frame
    ret, frame = cap.read()

    # Display the resulting frame
    cv2.imshow('frame', frame)

    # Wait for a key press and bind actions to specific keys
    key = cv2.waitKey(1) & 0xFF  # Wait for key press and get ASCII value

    # save frames
    out.write(frame)
    if key == ord('q'): 
        print("stop camera")
        cap.release()
        break
    elif key == ord(" "): 
        print("stop recording")
        out.release()

# When everything done, release the capture
out.release()
cap.release()
cv2.destroyAllWindows()