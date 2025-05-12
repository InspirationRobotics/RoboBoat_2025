import cv2
import depthai as dai
import numpy as np

# Global clicked point
clicked_point = [-1, -1]

# Mouse event callback to store click
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_point[0], clicked_point[1] = x, y

def main():
    # Create DepthAI pipeline
    pipeline = dai.Pipeline()

    # Configure color camera
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
    cam_rgb.setInterleaved(False)

    # Output stream
    xout_rgb = pipeline.create(dai.node.XLinkOut)
    xout_rgb.setStreamName("color")
    cam_rgb.video.link(xout_rgb.input)

    # Initialize OpenCV window and callback
    cv2.namedWindow("Camera Stream")
    cv2.setMouseCallback("Camera Stream", mouse_callback)

    # Start pipeline
    with dai.Device(pipeline) as device:
        color_queue = device.getOutputQueue(name="color", maxSize=4, blocking=False)

        while True:
            in_frame = color_queue.get()
            frame = in_frame.getCvFrame()

            # Resize for display
            preview_frame = cv2.resize(frame, (960, 540))
            hsv_frame = cv2.cvtColor(preview_frame, cv2.COLOR_BGR2HSV)

            # Show HSV value if user clicked
            if clicked_point[0] != -1 and clicked_point[1] != -1:
                hsv_val = hsv_frame[clicked_point[1], clicked_point[0]]
                print(f"Clicked at ({clicked_point[0]}, {clicked_point[1]}) -> HSV: {hsv_val}")
                cv2.circle(preview_frame, (clicked_point[0], clicked_point[1]), 5, (0, 0, 255), -1)
                cv2.putText(preview_frame, f'HSV: {hsv_val}', (clicked_point[0] + 10, clicked_point[1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            cv2.imshow("Camera Stream", preview_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
