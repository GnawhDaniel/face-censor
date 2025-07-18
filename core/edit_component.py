from PyQt6.QtCore import Qt, QRunnable, pyqtSlot, QThreadPool, QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import (
    QLabel,
    QGridLayout,
    QWidget,
    QPushButton,
    QSizePolicy,
    QProgressBar
)
import numpy as np
import supervision as sv
import json

class EditComponent(QWidget):
    def __init__(self, parent=None):
        super(EditComponent, self).__init__(parent)
        self.parent = parent
        self.video = self.parent.censor.get_video_info()
        self.frame_gen = sv.get_video_frames_generator(source_path=self.video["path"])
        self.frame_num = 0

        self.parent.censor.load_overlay("assets/media/tracking.png")

        with open(".image_cache/data.json", 'r') as f:
            self.coords = json.load(f)

        # Initialize the video display label as an instance variable
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("border: 1px solid white;")
        self.video_label.setFixedWidth(400)
        self.video_label.setScaledContents(False)
        
        # Set up layout
        self.setup_ui()
        
        # Timer for frame updates (if you want to play video continuously)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
    def setup_ui(self):
        """Set up the user interface"""
        layout = QGridLayout()
        layout.addWidget(self.video_label, 0, 0)
        
        # Add play button
        play_button = QPushButton("Play Video")
        play_button.clicked.connect(self.play_video)
        layout.addWidget(play_button, 1, 0)
        
        self.parent.main_layout.addLayout(layout)
        
    def play_video(self):
        """Start playing the video"""
        # Reset the frame generator
        self.frame_gen = sv.get_video_frames_generator(source_path=self.video["path"])
        self.timer.start(self.video["video_info"].fps)
        
    def update_frame(self):
        """Update the current frame being displayed"""
        try:
            frame = next(self.frame_gen)
            coord = self.coords[self.frame_num]
            frame = self.parent.censor.censor(frame, coord)
            self.frame_num += 1
            self.display_frame(frame)
        except StopIteration:
            # Video finished
            self.timer.stop()
            
    def display_frame(self, frame):
        """Display a single frame"""

        # TODO: Move to init
        height, width, channel = self.video["video_info"].height, self.video["video_info"].width, 3
        bytesperline = channel * width
        #######################
        
        # Convert frame to QImage
        qImg = QImage(frame.data, width, height, bytesperline, QImage.Format.Format_RGB888).rgbSwapped()

        pixmap = QPixmap.fromImage(qImg)
        scaled_pixmap = pixmap.scaledToWidth(400, Qt.TransformationMode.SmoothTransformation)
        
        # Update the label
        self.video_label.setPixmap(scaled_pixmap)
        
    def stop_video(self, frame):
        """Stop video playback"""
        self.timer.stop()