from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel


class EncodeTab(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QHBoxLayout()
        main_layout.addWidget(QLabel("Encode tab"))

        self.setLayout(main_layout)


class DecodeTab(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QHBoxLayout()
        main_layout.addWidget(QLabel("Decode tab"))

        self.setLayout(main_layout)

