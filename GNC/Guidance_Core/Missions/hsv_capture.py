import cv2
import depthai as dai
import numpy as np

# Store all clicked points and their HSV values
clicked_points = []

# Mouse event callback to store click
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_points.append((x, y))

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

            hsv_values = []

            # Draw and collect HSV values
            for (x, y) in clicked_points:
                if 0 <= x < 960 and 0 <= y < 540:
                    hsv = hsv_frame[y, x]
                    hsv_values.append(hsv)
                    cv2.circle(preview_frame, (x, y), 5, (0, 0, 255), -1)
                    cv2.putText(preview_frame, f'{hsv}', (x + 10, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Show HSV stats
            if hsv_values:
                hsv_array = np.array(hsv_values)
                hsv_min = np.min(hsv_array, axis=0)
                hsv_max = np.max(hsv_array, axis=0)
                hsv_avg = np.mean(hsv_array, axis=0).astype(int)

                print("\n--- HSV Stats ---")
                print(f"Min: {hsv_min}")
                print(f"Max: {hsv_max}")
                print(f"Avg: {hsv_avg}")

                # Display stats on preview
                stats_text = f"Min: {hsv_min}  Max: {hsv_max}  Avg: {hsv_avg}"
                cv2.putText(preview_frame, stats_text, (10, 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 255, 50), 2)

            cv2.imshow("Camera Stream", preview_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
