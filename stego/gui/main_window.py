from PySide6.QtWidgets import QMainWindow

from stego.gui.coder_widget import CoderWidget


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stego coder")
        self.coder_widget = CoderWidget()
        self.setCentralWidget(self.coder_widget)
        self.resize(500, 300)
