from PySide6.QtWidgets import QMainWindow, QTabWidget

from stego.gui.decode.decoder_widget import DecoderWidget
from stego.gui.encode.encoder_widget import EncoderWidget


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tab_widget = QTabWidget(self)
        self.encoder_widget = EncoderWidget()
        self.decoder_widget = DecoderWidget()

        self.tab_widget.addTab(self.encoder_widget, "Encode")
        self.tab_widget.addTab(self.decoder_widget, "Decode")

        self.setWindowTitle("Steganography App")
        self.setCentralWidget(self.tab_widget)
        self.resize(1200, 600)
