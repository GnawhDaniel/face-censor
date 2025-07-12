# load libraries
from huggingface_hub import hf_hub_download
from ultralytics import YOLO
import cv2
import numpy as np
import math
import os
import supervision

def distance(x1, x2, y1, y2):

    return math.sqrt((x2-x1)**2 + (y2-y1)**2)


def bound(res, to_overlay):
    # Get detection center
    center = res.boxes[0].xywh[0][0:2]
    cx, cy = int(center[0]), int(center[1])

    # Compute top-left corner (center the overlay)
    x1 = max(cx - overlay_w // 2, 0)
    y1 = max(cy - overlay_h // 2, 0)

    # Ensure overlay fits within original image
    x2 = min(x1 + overlay_w, image.shape[1])
    y2 = min(y1 + overlay_h, image.shape[0])

    # Calculate Distance to update overlay
    # dist = distance(x2,prev_x2,y2,prev_y2)

    # if dist < DISTANCE: # Prevent weird jumps
        # Crop overlay if it would go out of bounds
    overlay_crop = to_overlay[:y2 - y1, :x2 - x1]

    return x1,x2,y1,y2,overlay_crop


### Parameters

FRAME_OVERLAY = 1 # For every x frames, detect new face position and keep attempting until success 
VIDEO_PATH = "/home/danie/Videos/IMG_0259.MOV"
PREVIEW_LENGTH = 10 #seconds
OVERLAY_PATH = "tracking.png"
# OVERLAY_PATH_GIF = "extracted_pngs"
GIF_FRAMES = 1 or len(os.listdir(OVERLAY_PATH_GIF))
IS_GIF = False

# Load overlay image
if IS_GIF:
    to_overlay_gif = [cv2.imread(os.path.join(OVERLAY_PATH_GIF, f"frame_{i}.png")) for i in range(GIF_FRAMES)]
    to_overlay = to_overlay_gif[0]
    overlay_h, overlay_w = to_overlay_gif[0].shape[:2]
else:
    to_overlay = cv2.imread(OVERLAY_PATH)
    overlay_h, overlay_w = to_overlay.shape[:2]

# Videowriter
cap = cv2.VideoCapture(VIDEO_PATH)
fps = cap.get(cv2.CAP_PROP_FPS)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cap.release()
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter('output.mp4',fourcc,fps,frameSize=(frame_width, frame_height))

# Load Model
model_path = hf_hub_download(repo_id="arnabdhar/YOLOv8-Face-Detection", filename="model.pt")
model = YOLO(model_path)

# Loop through results
results = model(VIDEO_PATH, stream=True)

x1,x2,y1,y2,overlay_crop = 0, 0, 0, 0, None # For first frame purposes

count = 0
frames = 0

for res in results:
    image = res.orig_img.astype(np.uint8)

    if IS_GIF:
        to_overlay = to_overlay_gif[frames % GIF_FRAMES]
    
    # Check for detections
    if (count >= FRAME_OVERLAY) and res.boxes and len(res.boxes) > 0:
        prev_x2,prev_y2 = x2, y2

        x1,x2,y1,y2,overlay_crop = bound(res, to_overlay)

        count = 0

    # Overlay
    if x2: # If detection has occurred before
        if (IS_GIF):
            image[y1:y2, x1:x2] = to_overlay[:y2 - y1, :x2 - x1]
        else:
            image[y1:y2, x1:x2] = overlay_crop

    # Save or display result
    # cv2.imshow("Overlay Result", image)
    video.write(image)

    # Allow user to quit early
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    count += 1
    frames += 1

