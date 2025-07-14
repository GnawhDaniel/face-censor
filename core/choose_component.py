from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QPushButton,
)

class ChooseWidgets():
    def __init__(self, icon_path, text, event_handler):
        icon = QIcon(icon_path)
        self.button = QPushButton()
        self.button.setIcon(icon)
        self.button.setIconSize(QSize(200, 200))
        self.button.setFixedSize(200, 200)
        self.button.setStyleSheet("border: none;")
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.clicked.connect(event_handler)

        self.prompt = QLabel(text)
        self.prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prompt.setStyleSheet("color: white; font-size: 18px;")
    
    def get_widget(self):
        return self.button, self.prompt

