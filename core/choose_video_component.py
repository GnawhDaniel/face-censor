from multiprocessing import process
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import (
    QLabel,
    QGridLayout,
    QFileDialog,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout
)
from sympy import true
from core.choose_component import ChooseWidgets
import os
from utils.delete_layout import reset_window

class ChooseVideoComponent(QWidget):
    def __init__(self, parent=None):
        super(ChooseVideoComponent, self).__init__(parent)
        self.parent = parent

        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(50)
        
        # Pick Video File
        vid_widget = ChooseWidgets(
            icon_path="assets/svg-repo/video-file.svg",
            text="Choose Video File",
            event_handler=self._on_video_button_clicked
        )
        btn, prompt = vid_widget.get_widget()
        self.content_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(prompt, alignment=Qt.AlignmentFlag.AlignCenter)
        self.parent.main_layout.addLayout(self.content_layout)
    
    def _on_video_button_clicked(self):
        self.video_path = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "/home",
            "Video Files (*.mp4 *.avi *.mov)"
        )

        # Check if file exists
        if os.path.exists(self.video_path[0]):
            print("self.video_path:", self.video_path[0])
            # Load the video into the CensorFace instance
            self.parent.censor.load_video(self.video_path[0])
            self._update_video_info()

    def _update_video_info(self):
        # Remove existing widgets
        while self.content_layout.count():
            item = self.content_layout.itemAt(0)
            # Remove existing widgets
            widget = item.widget()
            if widget is not None:
                self.content_layout.removeWidget(widget)
                widget.deleteLater()

        sub_layout = QHBoxLayout()
        sub_layout.setSpacing(25)

        # Set new layout
        vid_info_dict = self.parent.censor.get_video_info()
        vid_info = vid_info_dict["video_info"]
        thumbnail = vid_info_dict["thumbnail"]
        vid_path = vid_info_dict["path"]

        # Set video thumbnail 
        height, width, channel = thumbnail.shape
        bytesperline = channel * width
        qImg = QImage(thumbnail.data, width, height, bytesperline, QImage.Format.Format_RGB888).rgbSwapped()
        label = QLabel()
        pixmap = QPixmap.fromImage(qImg)
        scaled_pixmap = pixmap.scaledToWidth(400, Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(scaled_pixmap)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        label.setStyleSheet("border: 1px solid white;")
        label.setFixedWidth(400)
        label.setScaledContents(False)  # Important: don't stretch!

        # Set Video Metadata Information
        duration_seconds = int(vid_info.total_frames / vid_info.fps)
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60
        qlabel = QLabel(
            f"{vid_path}\n\n"
            f"Aspect Ratio: {vid_info.width}x{vid_info.height}\n"  # Assuming width and height are available
            f"Duration: {minutes:02d}:{seconds:02d}\n"
            f"FPS: {vid_info.fps}\n"
            f"Total Frames: {vid_info.total_frames}\n"
        )
        qlabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # qlabel.setFixedWidth(400)  # Match image width if needed

        # Set Widgets
        sub_layout.addWidget(qlabel, alignment=Qt.AlignmentFlag.AlignCenter)
        sub_layout.addWidget(label,alignment=Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addLayout(sub_layout)

        # Set Process Button
        process_button = QPushButton("Process Video!")
        self.content_layout.addWidget(process_button)

        process_button.clicked.connect(lambda: self._remove_process_button(process_button))
        process_button.clicked.connect(self.parent._start_process)
    
    def _remove_process_button(self, process_button):
        self.content_layout.removeWidget(process_button)
        process_button.setParent(None)
        process_button.deleteLater()


    def get_layout(self):
        return self.content_layout