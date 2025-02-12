import cv2

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

if(cap.isOpened):
    print("capture exist")

while(True):
    ret,frame = cap.read()

    cv2.imshow("frame",frame)
    print("Just executed image show")

    key = cv2.waitKey(1) & 0xFF  

    if key == ord('q'):
        print("stop camera")
        cap.release()
        break


    