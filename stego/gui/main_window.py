from PySide6.QtWidgets import QMainWindow

from stego.gui.coder_widget import CoderWidget
from stego.gui.comparison.difference_viewer import DifferenceImageViewer


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stego coder")
        self.coder_widget = CoderWidget()
        self.comparison_widget = DifferenceImageViewer()
        self.setCentralWidget(self.comparison_widget)
        self.resize(500, 300)
