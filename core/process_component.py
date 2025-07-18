from PyQt6.QtCore import Qt, QRunnable, pyqtSlot, QThreadPool, QObject, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage

from PyQt6.QtWidgets import (
    QLabel,
    QGridLayout,
    QWidget,
    QPushButton,
    QSizePolicy,
    QProgressBar
)
import time
from multiprocessing import Process
from utils.delete_layout import reset_window



class ProcessMonitorWorker(QRunnable):
    def __init__(self, process):
        super().__init__()
        self.process = process

    @pyqtSlot()
    def run(self):
        # Poll the process status in a loop
        while self.process.is_alive():
            time.sleep(0.1)  # Sleep 100ms between checks

        # Join to clean up system resources
        self.process.join()

class WorkerSignals(QObject):
    result = pyqtSignal(int)

class Worker(QRunnable):
    def __init__(self, get_frame, *args, **kwargs):
        super().__init__()
        self.get_frame = get_frame
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()    

    @pyqtSlot()
    def run(self):
        value = self.get_frame().value
        max_val = self.kwargs["maximum"]
        while value < max_val:
            time.sleep(0.1)
            value = self.get_frame().value
            self.signals.result.emit(value)

class ProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 100)
        self.setValue(0)
        self.setTextVisible(True)

    def update_progress(self, value):
        self.setValue(value)

class ProcessComponent(QWidget):
    def __init__(self, parent=None):
        super(ProcessComponent, self).__init__(parent)
        self.parent = parent

        # Concurrency for progress bar 
        self.threadpool = QThreadPool()

        self.process = None

        self.censor = parent.censor
        self.progress_bar = ProgressBar(self)
        self.progress_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        # parent.main_layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)

        # Initialize the layout
        self.process_layout = QGridLayout()
        self.process_layout.setSpacing(0)

        # for col in range(2):
        #     self.process_layout.setColumnStretch(col, 1)

        qlabel = QLabel("Processing Video...")
        self.process_layout.addWidget(qlabel, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.process_layout.addWidget(self.progress_bar)

        parent.main_layout.addLayout(self.process_layout)

        self.start_processing()

    def update_progress(self, value):
        """
        Update the progress bar with the current value.
        :param value: Current progress value.
        """

        decimal_value = value / self.censor.get_max_frames()
        percent_value = int(decimal_value * 100)

        self.progress_bar.setValue(percent_value)
        self.progress_bar.setFormat(f"{decimal_value:.2%}")

        if decimal_value == 1:
            edit_button = QPushButton("Edit Video")
            edit_button.clicked.connect(self.parent._start_editing) #TODO: Clear all layouts and widgets and move to next screen
            self.process_layout.addWidget(edit_button)
            

    def start_processing(self):
        # Start the worker in a separate thread

        self.process = Process(target=self.censor.execute)
        self.process.start()
        monitor_worker = ProcessMonitorWorker(self.process)
        self.threadpool.start(monitor_worker)

        worker = Worker(self.censor.get_processed_frames, maximum=self.censor.get_max_frames())
        worker.signals.result.connect(self.update_progress)
        self.threadpool.start(worker)

    def get_process(self):
        return self.process