from PySide6.QtWidgets import *
import sys
import os


class FaceDecensorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Censor")

        self.setGeometry(0,0,1280,720)
        
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        open_action = file_menu.addAction("Open")
        open_action.triggered.connect(self.open_file)

    def open_file(self):
        file_name = QFileDialog.getOpenFileName(self,
            self.tr("Open Image"), "/home/", self.tr("Video Files (*.mp4)")) # TODO: Handle OS directory


def main():
    # print(os.name)

    app = QApplication(sys.argv)
    window = FaceDecensorApp()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
