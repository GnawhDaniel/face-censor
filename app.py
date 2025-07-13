from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QLabel,
    QMainWindow,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QFileDialog
)
from core.censorface import CensorFace
from core.choose_component import Choose
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Censify v1.0")
        self.setMinimumSize(QSize(1000, 600))
        self.setStyleSheet("background-color: #2D2D2D;")

        self.output_path = ""
        self.video_path = ""

        # Toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Layout
        self.main_layout = QHBoxLayout()
        self.main_layout.setSpacing(50)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Pick Video File
        video_choose = Choose(
            icon_path="assets/svg-repo/video-file.svg",
            text="Choose Video File",
            event_handler=self.on_video_button_clicked
        )
        self.main_layout.addLayout(video_choose.get_layout())

        
        # Pick Overlay File
        overlay_choose = Choose(
            icon_path="assets/svg-repo/add-image.svg",
            text="Choose Overlay File",
            event_handler=lambda: print("Overlay file chosen")  # Placeholder for overlay logic
        )
        self.main_layout.addLayout(overlay_choose.get_layout())

        # Bottom most widget
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

        # Censoring Logic
        # TODO: may have to create separate thread for this
        self.censor = CensorFace(
            frame_overlay=0,
            output_path=self.output_path
        )

    def on_video_button_clicked(self):
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

    def on_overlay_button_clicked(self):
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
            


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()