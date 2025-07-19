from PyQt6.QtCore import QSize, Qt, QObject, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QHBoxLayout
)
from core.start_component import StartWindow
from core.choose_overlay_component import OverlayComponent
from core.process_component import ProcessComponent
from core.censorface import CensorFace
from utils.delete_layout import reset_window
from core.choose_video_component import ChooseVideoComponent
from core.edit_component import EditComponent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Censify v1.0")
        self.setMinimumSize(QSize(1000, 600))
        self.setStyleSheet("background-color: #2D2D2D;")

        self.output_path = "output/censored_video.mp4"  # Default output path
        self.process = None
        
        self.overlay = None

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
        self.widget = QWidget()
        self.widget.setLayout(self.main_layout)
        self.setCentralWidget(self.widget)

        self.censor = CensorFace(
            frame_overlay=3,  # Default frame overlay
            output_path=self.output_path
        )

        QApplication.instance().aboutToQuit.connect(self._cleanup_processing_model)

        # Main Content
        # StartWindow(self)
        _component = ChooseVideoComponent(self)

        # TODO: Remove
        debug_action.triggered.connect(lambda: (self.censor.load_video("/home/danie/Videos/untitled.mp4"), self._start_editing()))
        toolbar.addAction(debug_action)

    def _cleanup_processing_model(self):
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
    
    def _start_editing(self):
        reset_window(self.main_layout)

        # self.widget.setLayout(None)
        # self.widget.setLayout(None)
        self.overlay = OverlayComponent(self)
        EditComponent(self)



def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()