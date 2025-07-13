from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QPushButton,
)

class Choose():
    def __init__(self, icon_path, text, event_handler):
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QIcon(icon_path)
        button = QPushButton()
        button.setIcon(icon)
        button.setIconSize(QSize(200, 200))
        button.setFixedSize(200, 200)
        button.setStyleSheet("border: none;")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.layout.addWidget(button)
        button.clicked.connect(event_handler)


        prompt = QLabel(text)
        prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prompt.setStyleSheet("color: white; font-size: 18px;")
        self.layout.addWidget(prompt)
    
    def get_layout(self):
        return self.layout