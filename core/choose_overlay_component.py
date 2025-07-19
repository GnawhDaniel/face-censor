from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFileDialog
)
from core.choose_component import ChooseWidgets
import os
from utils.delete_layout import reset_window


class OverlayComponent(QWidget):
    def __init__(self, parent=None):
        super(OverlayComponent, self).__init__(parent)
        self.parent = parent
        print(self.parent.main_layout)

        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(0)

        # Pick Video File
        overlay_widget = ChooseWidgets(
            icon_path="assets/svg-repo/add-image.svg",
            text="Choose Overlay Image",
            event_handler=self._on_overlay_button_clicked
        )

        self.btn, self.prompt = overlay_widget.get_widget()
        self.content_layout.addWidget(self.btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.prompt, alignment=Qt.AlignmentFlag.AlignCenter)
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
            print(self.overlay_path)
            self.parent.censor.load_overlay(self.overlay_path[0])
            self.prompt.setText("Change Overlay Image")
            # self.overlay_path.setLabelText("Change Overlay Image")
            self._update_image(self.overlay_path[0])

    def _update_image(self, image_path):
        """
        Update overlay image to user selected.
        """
        overlay_widget = ChooseWidgets(
            icon_path=image_path,
            text="Change Overlay Image",
            event_handler=self._on_overlay_button_clicked
        )

        reset_window(self.content_layout)
        self.btn, self.prompt = overlay_widget.get_widget()
        self.btn.setIconSize(QSize(250, 250))
        self.btn.setFixedSize(250, 250)
        self.content_layout.addWidget(self.btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.prompt, alignment=Qt.AlignmentFlag.AlignCenter)
