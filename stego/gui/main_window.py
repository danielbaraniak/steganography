from PySide6.QtWidgets import QMainWindow, QTabWidget

from stego.gui.tabs import EncodeTab, DecodeTab


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PADAWANS")

        self.tabs = QTabWidget()

        self.tab1 = EncodeTab()
        self.tab2 = DecodeTab()

        self.tabs.addTab(self.tab1, "Encode")
        self.tabs.addTab(self.tab2, "Decode")

        self.setCentralWidget(self.tabs)
