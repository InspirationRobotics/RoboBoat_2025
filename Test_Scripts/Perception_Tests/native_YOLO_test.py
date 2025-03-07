from ultralytics import YOLO

# Load a model
model = YOLO("MHS_SEALS_V14.pt")  # pretrained YOLO11n model

# Run batched inference on a list of images
results = model(["IMG_0797.JPEG", "IMG_0798.JPEG"])  # return a list of Results objects

image_number = 0
# Process results list
for result in results:
    boxes = result.boxes  # Boxes object for bounding box outputs
    masks = result.masks  # Masks object for segmentation masks outputs
    keypoints = result.keypoints  # Keypoints object for pose outputs
    probs = result.probs  # Probs object for classification outputs
    obb = result.obb  # Oriented boxes object for OBB outputs
    image_number +=1
    result.show()  # display to screen
    result.save(filename=f"result{image_number}.jpg")  # save to disk