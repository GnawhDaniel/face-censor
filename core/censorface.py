# load libraries
# from huggingface_hub import hf_hub_download
from ultralytics import YOLO
import cv2
import math
import os
import supervision as sv
import json


class CensorFace:
    @staticmethod
    def distance(x1, x2, y1, y2):
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)

    @staticmethod
    def bound(detection, overlay_img, overlay_w, overlay_h, image_shape: tuple):
        """
        Bound the overlay image to the detected face position and crop it if necessary.
        :param detection: The detection object containing the bounding box coordinates.
        :param overlay_img: The overlay image to be placed on the detected face.
        :param overlay_w: Width of the overlay image.
        :param overlay_h: Height of the overlay image.
        :param image_shape: Shape of the original image (height, width).
        :return: Coordinates for the overlay position and the cropped overlay image.
        """
        # Get detection center
        x1_det, y1_det, x2_det, y2_det = detection.xyxy[0][:4]
        cx = int((x1_det + x2_det) / 2)
        cy = int((y1_det + y2_det) / 2)    

        # Compute top-left corner (center the overlay)
        x1 = max(cx - overlay_w // 2, 0)
        y1 = max(cy - overlay_h // 2, 0)

        # Ensure overlay fits within original image
        x2 = min(x1 + overlay_w, image_shape[1])
        y2 = min(y1 + overlay_h, image_shape[0])

        # Calculate Distance to update overlay
        # dist = distance(x2,prev_x2,y2,prev_y2)

        # if dist < DISTANCE: # Prevent weird jumps
            # Crop overlay if it would go out of bounds
        overlay_crop = overlay_img[:y2 - y1, :x2 - x1]

        return x1,x2,y1,y2,overlay_crop
    
    def __init__(self, frame_overlay, output_path):
        """
        Initialize the CensorFace class with parameters for face detection and overlay.
        :param frame_overlay: Number of frames to wait before detecting a new face position.
        :param gif_frames: Number of frames in the gif.
        :param is_gif: Boolean indicating if the overlay is a gif.
        :param output_path: Path to save the output video.
        """

        # Create directories if it doesn't exist
        if not os.path.exists(".image_cache"):
            os.makedirs(".image_cache")

        # Initialize variables
        self.video_path = None # Path to the video file
        self.overlay_gif = []
        self.overlay_h = 0
        self.overlay_w = 0
        self.overlay_img = None
        self.gif_frames = 0
        self.is_gif = False # Whether the overlay is a gif or a static image
        self.tracker = None # Tracker for face detection
        self.smoother = None # Smoother for detections
        self.video_info = None
        self.frame_generator = None

        # Parameters
        self.frame_overlay = frame_overlay # For every x frames, detect new face position and keep attempting until success 
        self.output_path = output_path # Path to save the output video

        # Load Model
        # model_path = hf_hub_download(repo_id="arnabdhar/YOLOv8-Face-Detection", filename="model.pt")
        self.model = YOLO("models/yolov12l-face.pt")


    def load_video(self, video_path):
        """
        Load the video file for processing.
        :param video_path: Path to the video file.
        """
        self.video_path = video_path
        self.video_info = sv.VideoInfo.from_video_path(video_path=self.video_path)
        self.frame_generator = sv.get_video_frames_generator(source_path=self.video_path)
        self.tracker = sv.ByteTrack(frame_rate=self.video_info.fps)
        self.smoother = sv.DetectionsSmoother(length=3)

    def load_overlay(self, is_gif=False, overlay_path=None, gif_frames=0):
        # Load overlay image
        self.is_gif = is_gif
        if self.is_gif:
            self.overlay_gif = [cv2.imread(os.path.join(overlay_path, f"frame_{i}.png")) for i in range(self.gif_frames)]
            self.overlay_img = self.to_overlay_gif[0]
            self.gif_frames = gif_frames
            self.overlay_h, self.overlay_w = self.to_overlay_gif[0].shape[:2]
        else:
            self.overlay_img = cv2.imread(overlay_path)
            self.overlay_h, self.overlay_w = self.overlay_img.shape[:2]


    def execute(self):
        # Loop through results
        x1,x2,y1,y2,overlay_crop = 0, 0, 0, 0, None # For first frame purposes

        count = 0
        frame_count = 0
        coord_list = []

        to_overlay = self.to_overlay_gif[0] if self.is_gif else cv2.imread(self.overlay_path)

        with sv.VideoSink(self.output_path, video_info=self.video_info) as sink:
            for frame in self.frame_generator:
                # Logging
                print(f"{frame_count:05d}/{self.video_info.total_frames:05d} - {(frame_count / self.video_info.total_frames * 100):2.2f}%")

                res = self.model(frame,verbose=False)[0]
                image = frame

                if self.is_gif:
                    to_overlay = self.overlay_gif[frame_count % self.gif_frames]
                
                # Check for detections
                if (count >= self.frame_overlay):
                    detections = sv.Detections.from_ultralytics(res)
                    detections = self.tracker.update_with_detections(detections)
                    detections = self.smoother.update_with_detections(detections)

                    if detections.xyxy.size > 0:
                        x1,x2,y1,y2,overlay_crop = CensorFace.bound(detections, to_overlay, self.overlay_w, self.overlay_h, (image.shape[0], image.shape[1]))
                        count = 0

                # Overlay
                if x2: # If detection has occurred before
                    if (self.is_gif):
                        image[y1:y2, x1:x2] = to_overlay[:y2 - y1, :x2 - x1]
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



