# load libraries
# from huggingface_hub import hf_hub_download
from ultralytics import YOLO
import cv2
import math
import os
import supervision as sv
import json
from multiprocessing import Value


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
        x1_det, y1_det, x2_det, y2_det = detection
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
        self.overlay_path = None
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

        self.processed_frames = Value("i", 0) # Number of processed frames

        # Parameters
        self.frame_overlay = frame_overlay # For every x frames, detect new face position and keep attempting until success 
        self.output_path = output_path # Path to save the output video

        # Load Model
        # model_path = hf_hub_download(repo_id="arnabdhar/YOLOv8-Face-Detection", filename="model.pt")
        self.model = YOLO("models/yolov12l-face.pt")

    def get_video_info(self):
        """
        Get the path to the video file.
        :return: Path to the video file.
        """

        if not self.video_path:
            return {}
        
        _temp = sv.get_video_frames_generator(source_path=self.video_path)
        thumbnail = next(_temp) if _temp else None
        del _temp

        info = {
            "video_info": self.video_info,
            "path": self.video_path,
            "thumbnail": thumbnail,
        }
        return info

    def get_overlay_path(self):
        """
        Get the path to the overlay image or gif.
        :return: Path to the overlay image or gif.
        """
        return self.overlay_path

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

    def load_overlay(self, overlay_path=None,is_gif=False, gif_frames=0):
        # Load overlay image
        self.is_gif = is_gif
        self.overlay_path = overlay_path
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
        x1,x2,y1,y2 = 0, 0, 0, 0 # For first frame purposes

        count = 0
        frame_count = 0
        coord_list = []

        for frame in self.frame_generator:

            res = self.model(frame,verbose=False)[0]

            # Check for detections
            if (count >= self.frame_overlay):
                detections = sv.Detections.from_ultralytics(res)
                detections = self.tracker.update_with_detections(detections)
                detections = self.smoother.update_with_detections(detections)
                if detections:
                    x1, y1, x2, y2 = detections.xyxy[0][:4]

            # Save or display result
            frame_coords = {"frame": frame_count, 
                            "coords": 
                                {"x1": float(x1), 
                                 "x2": float(x2), 
                                 "y1": float(y1), 
                                 "y2": float(y2)}}
            
            coord_list.append(frame_coords)

            count += 1
            frame_count += 1
            self.processed_frames.value += 1

        with open(".image_cache/data.json", 'w') as file:
            json.dump(coord_list, file, indent=4)

    def get_processed_frames(self):
        """
        Get the number of processed frames.
        :return: Number of processed frames.
        """
        return self.processed_frames

    def get_max_frames(self):
        """
        Get the maximum number of frames in the overlay gif.
        :return: Maximum number of frames in the overlay gif.
        """
        return self.video_info.total_frames

    def censor(self, frame, coord):
        # return frame

        x1 = coord["coords"]["x1"]
        x2 = coord["coords"]["x2"]
        y1 = coord["coords"]["y1"]
        y2 = coord["coords"]["y2"]
        
        x1,x2,y1,y2,overlay_crop = CensorFace.bound([x1,y1,x2,y2], 
                                                    self.overlay_img, 
                                                    self.overlay_w, 
                                                    self.overlay_h, 
                                                    (frame.shape[0], frame.shape[1])
                                                    )

        frame[y1:y2, x1:x2] = overlay_crop
        return frame