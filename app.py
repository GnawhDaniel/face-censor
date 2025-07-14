from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QPixmap, QImage
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QToolBar,
    QVBoxLayout,
    QPushButton,
    QGridLayout,
    QWidget,
    QFileDialog
)
from core.censorface import CensorFace
from core.choose_component import ChooseWidgets
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Censify v1.0")
        self.setMinimumSize(QSize(1000, 600))
        self.setStyleSheet("background-color: #2D2D2D;")

        # State
        self.video_set = False
        self.overlay_set = False
        self.output_path = "output/censored_video.mp4"  # Default output path

        # Layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Main Content
        self.content_layout = QGridLayout()
        self.content_layout.setSpacing(0)  # Set to 0 for no vertical/horizontal spacing
        for col in range(2):
            self.content_layout.setColumnStretch(col, 1)
        # for row in range(2):
        #     self.content_layout.setRowStretch(row, 1)

        # Pick Video File
        vid_widget = ChooseWidgets(
            icon_path="assets/svg-repo/video-file.svg",
            text="Choose Video File",
            event_handler=self._on_video_button_clicked
        )
        btn, prompt = vid_widget.get_widget()
        self.content_layout.addWidget(btn, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(prompt, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)

        # Pick Overlay File
        overlay_widget = ChooseWidgets(
            icon_path="assets/svg-repo/add-image.svg",
            text="Choose Overlay File",
            event_handler=self._on_overlay_button_clicked  # Placeholder for overlay logic
        )
        btn, prompt = overlay_widget.get_widget()
        self.content_layout.addWidget(btn, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(prompt, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add content layout to main layout
        self.main_layout.addLayout(self.content_layout)

        # Bottom most widget
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

        # Toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        debug_action = QAction("Debug", self)
        debug_action.triggered.connect(lambda: self._reset_window(self.main_layout))
        
        debug_action2 = QAction("Get Layout Count", self)
        debug_action2.triggered.connect(lambda: print(f"Layout count: {self.main_layout.count()}"))
        toolbar.addAction(debug_action)
        toolbar.addAction(debug_action2)


        # Censoring Logic
        # TODO: may have to create separate thread for this
        self.censor = CensorFace(
            frame_overlay=0,
            output_path=self.output_path
        )

    @staticmethod
    def _reset_window(layout):
        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()
            if widget is not None:
                layout.removeWidget(widget)
                widget.deleteLater()

            elif item.layout():
                MainWindow._reset_window(item.layout())

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
            self.censor.load_video(self.video_path[0])
            self._update_video_info()

    def _update_video_info(self):
        # Remove existing widgets
        for i in range(2):
            item = self.content_layout.itemAtPosition(i, 0)
            # Remove existing widgets
            widget = item.widget()
            if widget is not None:
                self.content_layout.removeWidget(widget)
                widget.deleteLater()

        # Set new layout
        vid_info_dict = self.censor.get_video_info()
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
        self.content_layout.addWidget(label, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)

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
        self.content_layout.addWidget(qlabel, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)

        self.video_set = True
        # Check States
        self._check_user_input()

    def _check_user_input(self):
        # TODO: validate mask is small enough
        if self.video_set and self.overlay_set:
            # Show Process Button
            process_button = QPushButton("Process Video")
            self.main_layout.addWidget(process_button, alignment=Qt.AlignmentFlag.AlignCenter)
            process_button.clicked.connect(lambda: MainWindow._reset_window(self.main_layout))  # Placeholder for processing logic

    def _on_overlay_button_clicked(self):
        self.overlay_path = QFileDialog.getOpenFileName(
            self,
            "Select Overlay File",
            "/home",
            "Image Files (*.png *.jpg *.jpeg *.gif)"
        )
        # Check if file exists
        if os.path.exists(self.overlay_path[0]):
            # Check if gif
            if self.overlay_path[0].endswith('.gif'):
                # TODO: Handle GIF loading
                pass
            else:
                # Load the overlay into the CensorFace instance
                self.censor.load_overlay(overlay_path=self.overlay_path[0])
                self._update_overlay_info() 
    
    def _update_overlay_info(self):
        # Remove existing widgets
        for i in range(2):
            item = self.content_layout.itemAtPosition(i, 1)
            widget = item.widget()
            if widget is not None:
                self.content_layout.removeWidget(widget)
                widget.deleteLater()

        # Set new layout
        overlay_path = self.censor.get_overlay_path()
        label = QLabel()
        pixmap = QPixmap(overlay_path)
        scaled_pixmap = pixmap.scaledToWidth(400, Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(scaled_pixmap)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        label.setStyleSheet("border: 1px solid white;")
        label.setFixedWidth(400)
        label.setScaledContents(False)  # Important: don't stretch!
        self.content_layout.addWidget(label, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        text = QLabel(f"{overlay_path}\n\n")
        text.setAlignment(Qt.AlignmentFlag.AlignLeft)
        text.setWordWrap(True)
        self.content_layout.addWidget(text, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.overlay_set = True
        # Check States
        self._check_user_input()


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()