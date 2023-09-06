from PySide6.QtWidgets import QMainWindow

from stego.gui.encode.encoder_widget import EncoderWidget
from stego.gui.comparison.image_comparison_widget import ImageComparisonWidget


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stego coder")
        self.coder_widget = EncoderWidget()
        self.comparison_widget = ImageComparisonWidget()

        self.setCentralWidget(self.coder_widget)
        self.resize(1200, 600)
