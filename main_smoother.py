# load libraries
from huggingface_hub import hf_hub_download
from ultralytics import YOLO
import cv2
import numpy as np
import math
import os
import supervision as sv
import json

def distance(x1, x2, y1, y2):

    return math.sqrt((x2-x1)**2 + (y2-y1)**2)


def bound(detection, overlay_img, overlay_w, overlay_h):
    # Get detection center
    x1_det, y1_det, x2_det, y2_det = detection.xyxy[0][:4]
    cx = int((x1_det + x2_det) / 2)
    cy = int((y1_det + y2_det) / 2)    

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
    overlay_crop = overlay_img[:y2 - y1, :x2 - x1]

    return x1,x2,y1,y2,overlay_crop


### Parameters

FRAME_OVERLAY = 0 # For every x frames, detect new face position and keep attempting until success 
VIDEO_PATH = "/home/danie/Videos/IMG_0259.MOV"
PREVIEW_LENGTH = 10 #seconds
OVERLAY_PATH = "tracking.png"
OVERLAY_PATH_GIF = "extracted_pngs"
# GIF_FRAMES = len(os.listdir(OVERLAY_PATH_GIF))
GIF_FRAMES = 1
IS_GIF = False

# Load overlay image
if IS_GIF:
    to_overlay_gif = [cv2.imread(os.path.join(OVERLAY_PATH_GIF, f"frame_{i}.png")) for i in range(GIF_FRAMES)]
    to_overlay = to_overlay_gif[0]
    overlay_h, overlay_w = to_overlay_gif[0].shape[:2]
else:
    overlay_img = cv2.imread(OVERLAY_PATH)
    overlay_h, overlay_w = overlay_img.shape[:2]

# Videowriter
video_info = sv.VideoInfo.from_video_path(video_path="/home/danie/Videos/IMG_0259.MOV")
frame_generator = sv.get_video_frames_generator(source_path="/home/danie/Videos/IMG_0259.MOV")

# Load Model
# model_path = hf_hub_download(repo_id="arnabdhar/YOLOv8-Face-Detection", filename="model.pt")
model = YOLO("yolov12l-face.pt")
tracker = sv.ByteTrack(frame_rate=video_info.fps)
smoother = sv.DetectionsSmoother(length=3)

# Loop through results
x1,x2,y1,y2,overlay_crop = 0, 0, 0, 0, None # For first frame purposes

count = 0
frame_count = 0
coord_list = []

with sv.VideoSink("/home/danie/Projects/Face-Censor/output_smooth.mp4", video_info=video_info) as sink:
    for frame in frame_generator:
        # Logging
        print(f"{frame_count:05d}/{video_info.total_frames:05d} - {(frame_count / video_info.total_frames * 100):2.2f}%")

        res = model(frame,verbose=False)[0]
        image = frame

        if IS_GIF:
            to_overlay = to_overlay_gif[frame_count % GIF_FRAMES]
        
        # Check for detections
        if (count >= FRAME_OVERLAY):
            prev_x2,prev_y2 = x2, y2

            detections = sv.Detections.from_ultralytics(res)
            detections = tracker.update_with_detections(detections)
            detections = smoother.update_with_detections(detections)

            if detections.xyxy.size > 0:
                x1,x2,y1,y2,overlay_crop = bound(detections, overlay_img, overlay_w, overlay_h)

                count = 0

        # Overlay
        if x2: # If detection has occurred before
            if (IS_GIF):
                image[y1:y2, x1:x2] = overlay_img[:y2 - y1, :x2 - x1]
            else:
                image[y1:y2, x1:x2] = overlay_crop

        # Save or display result
        # cv2.imshow("Overlay Result", image)

        frame_coords = {"frame": frame_count, "coords": {"x1":x1, "x2":x2, "y1":y1, "y2":y2}}
        coord_list.append(frame_coords)

        sink.write_frame(image)

        # Allow user to quit early
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        count += 1
        frame_count += 1

    file = open(".image_cache/data.json", 'w')
    json.dump(coord_list, file, indent=4)
    file.close()
