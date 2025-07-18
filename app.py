from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from core.start_component import StartWindow
from core.process_component import ProcessComponent
from core.censorface import CensorFace
from utils.delete_layout import reset_window


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Censify v1.0")
        self.setMinimumSize(QSize(1000, 600))
        self.setStyleSheet("background-color: #2D2D2D;")

        self.output_path = "output/censored_video.mp4"  # Default output path
        self.process = None

        # Toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        debug_action = QAction("Debug", self)
        
        debug_action2 = QAction("Get Layout Count", self)
        debug_action2.triggered.connect(lambda: print(f"Layout count: {self.main_layout.count()}"))
        toolbar.addAction(debug_action2)

        # Layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Bottom most widget
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

        self.censor = CensorFace(
            frame_overlay=3,  # Default frame overlay
            output_path=self.output_path
        )

        QApplication.instance().aboutToQuit.connect(self.cleanup)

        # Main Content
        StartWindow(self)


        # TODO: Remove
        debug_action.triggered.connect(lambda: (reset_window(self.main_layout), self._start_process()))
        toolbar.addAction(debug_action)

    def cleanup(self):
        # TODO: make variables less confusing lol
        # process is the multiprocessing Processor object
        # self.process points to the ProcessComponent
        if self.process and self.process.process:
            process = self.process.get_process()
            if process:
                process.terminate()
                process.join()
    
    def _start_process(self):
        self.process = ProcessComponent(self)
        
    

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()