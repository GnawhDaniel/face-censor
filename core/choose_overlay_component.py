from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFileDialog
)
from core.choose_component import ChooseWidgets
import os


class OverlayComponent(QWidget):
    def __init__(self, parent=None):
        super(OverlayComponent, self).__init__(parent)
        self.parent = parent
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(25)

        # Pick Video File
        overlay_widget = ChooseWidgets(
            icon_path="assets/svg-repo/add-image.svg",
            text="Choose Overlay Image",
            event_handler=self._on_overlay_button_clicked
        )

        btn, prompt = overlay_widget.get_widget()
        self.content_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(prompt, alignment=Qt.AlignmentFlag.AlignCenter)
        self.parent.main_layout.addLayout(self.content_layout)

    def _on_overlay_button_clicked(self):
        self.overlay_path = QFileDialog.getOpenFileName(
            self,
            "Select Overlay File",
            "/home",
            "Image Files (*.png *.jpg *.jpeg *.gif)"
        )

        # Check if file exists
        if os.path.exists(self.overlay_path[0]):
            # Load the video into the CensorFace instance
            self.parent.censor.load_overlay(self.overlay_path[0])