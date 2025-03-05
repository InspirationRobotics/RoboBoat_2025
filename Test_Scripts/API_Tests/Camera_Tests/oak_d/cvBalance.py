import cv2
import numpy as np

video_path = "/home/chaser/Downloads/RoboBoat data/02_h264.mp4"
cap = cv2.VideoCapture(video_path)

# Parameters
num_reference_frames = 10
ref_y_values = []

# Get video properties
frame_count = 0
fps = cap.get(cv2.CAP_PROP_FPS)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_size = (frame_width, frame_height)  # Corrected way to get frame size

# Create VideoWriter object
out = cv2.VideoWriter(f"{video_path}_balanced.mp4", 
                      cv2.VideoWriter_fourcc(*'mp4v'), 
                      fps, frame_size)

def balance(frame,reference_Y_mean):
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

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break  # Stop if video ends

    # Extract the top 10% of the frame
    height, width, _ = frame.shape
    top_region = frame[:height // 10, :, :]

    # Convert to YCrCb and get the Y channel
    ycrcb = cv2.cvtColor(top_region, cv2.COLOR_BGR2YCrCb)
    Y_channel = ycrcb[:, :, 0]

    if frame_count < num_reference_frames:
        ref_y_values.append(Y_channel.mean())  # Store brightness values
        frame_count += 1
        if frame_count == num_reference_frames:
            reference_Y_mean = np.mean(ref_y_values)  # Compute the final reference brightness
            print(f"Reference Y Mean: {reference_Y_mean}")
    else:
        print(reference_Y_mean)
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

        # Display results
        cv2.imshow("Original", frame)
        cv2.imshow("Balanced", balanced)

    # Keyboard Controls
    key = cv2.waitKey(30) & 0xFF
    if key == ord('q'):
        break
    elif key == ord(' '):  # Pause/Resume
        paused = not paused

out.release()
cap.release()
cv2.destroyAllWindows()
