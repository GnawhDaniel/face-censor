from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import (
    QLabel,
    QGridLayout,
    QWidget,
)

class ProcessComponent(QWidget):
    def __init__(self, parent=None):
        super(ProcessComponent, self).__init__(parent)
        self.parent = parent

        # Initialize the layout
        self.process_layout = QGridLayout()
        self.process_layout.setSpacing(0)

        for col in range(2):
            self.process_layout.setColumnStretch(col, 1)

        qlabel = QLabel("Processing Video...")
        self.process_layout.addWidget(qlabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)

        parent.main_layout.addLayout(self.process_layout)