from os import path

import cv2
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFileDialog, QPushButton, QVBoxLayout, QMessageBox, \
    QScrollArea, QGroupBox, QGridLayout, QSlider, QLineEdit

from stego.coder.image_coder import RobustStegoCoder
from stego.coder.transform.dwt import Dwt


class EncodeTab(QWidget):
    def __init__(self):
        super().__init__()

        self.image_path_label = QLabel()
        self.compression_quality_slider = QSlider(self)
        self.compression_quality_label = QLabel()
        self.message_field = QLineEdit()
        self.open_image_button = QPushButton("Open")
        self.open_image_button.clicked.connect(self.open_image)

        self.encode_button = QPushButton("Encode")
        self.encode_button.clicked.connect(self.encode)
        self.encode_button.setEnabled(False)

        self.decode_button = QPushButton("Decode")
        self.decode_button.clicked.connect(self.decode)
        self.decode_button.setEnabled(False)

        self.image_widget = QLabel()
        self.image_widget.setScaledContents(True)

        self.image_scroll_area = QScrollArea()
        self.image_scroll_area.setWidget(self.image_widget)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.create_image_preview_box())
        main_layout.addLayout(self.create_coder_controls())

        self.setLayout(main_layout)

    def create_image_preview_box(self):

        image_box = QGroupBox("Image preview")

        layout = QVBoxLayout()

        layout.addWidget(self.image_scroll_area)

        image_box.setLayout(layout)

        return image_box

    def create_coder_controls(self):

        self.compression_quality_slider.setMinimum(10)
        self.compression_quality_slider.setMaximum(100)
        self.compression_quality_slider.setSingleStep(1)
        self.compression_quality_slider.setOrientation(Qt.Horizontal)
        self.compression_quality_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.compression_quality_slider.valueChanged.connect(
            lambda: self
            .compression_quality_label
            .setText(str(self.compression_quality_slider.value()))
        )
        self.compression_quality_slider.setValue(70)

        self.image_path_label.setWordWrap(True)

        encoder_info = [
            ("Path", self.image_path_label, self.open_image_button),
            ("Compression quality", self.compression_quality_slider, self.compression_quality_label),
            ("Message", self.message_field, QLabel()),
        ]

        grid = QGridLayout()

        for i, (name, widget1, widget2) in enumerate(encoder_info):
            grid.addWidget(QLabel(name), i, 0)
            grid.addWidget(widget1, i, 1)
            grid.addWidget(widget2, i, 2)

        buttons = QHBoxLayout()
        buttons.addWidget(self.decode_button)
        buttons.addWidget(self.encode_button)

        column = QVBoxLayout()
        column.addLayout(grid)
        column.addLayout(buttons)

        return column

    def open_image(self):
        file_name = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")

        image = None
        if file_name[0]:
            image = QImage(file_name[0])
            if image.isNull():
                self.encode_button.setEnabled(False)
                self.decode_button.setEnabled(False)
                QMessageBox.information(
                    self, "Image Viewer", f"Unable load {file_name[0]}.")
                return

        # Load in image pixmap
        self.image_widget.setPixmap(QPixmap.fromImage(image))
        self.image_widget.adjustSize()

        # update image path
        self.image_path_label.setText(file_name[0])

        self.encode_button.setEnabled(True)
        self.decode_button.setEnabled(True)

    def decode(self):
        print("in decode")
        stego_coder = RobustStegoCoder(
            Dwt('haar', level=3),
            levels_to_encode=1,
            alpha=1
        )

        input_path = self.image_path_label.text()

        print(input_path)

        image = cv2.imread(input_path)
        try:
            message = stego_coder.decode_color_image(image)
            print(message)
            if message:
                QMessageBox.information(self, "Hidden Message", message)
            else:
                QMessageBox.warning(self, "Decoding Error", f"Cannot find a message.")
        except Exception:
            QMessageBox.warning(self, "Decoding Error", f"Cannot find a message.")

    def encode(self):
        print("in encode")
        compression_quality = self.compression_quality_slider.value()
        message = self.message_field.text()
        input_path = self.image_path_label.text()

        output_path = QFileDialog.getSaveFileName(
            self, "Save Image", "", "Image Files (*.jpg)")

        if output_path[0]:
            output_path = output_path[0]

            filename, file_extension = path.splitext(output_path)
            if not file_extension:
                output_path = filename + ".jpg"
        else:
            return

        image = cv2.imread(input_path)
        stego_coder = RobustStegoCoder(
            Dwt('haar', level=3),
            levels_to_encode=1,
            quality_level=compression_quality,
            alpha=1
        )
        stego_image = stego_coder.encode_color_image(image, message)

        cv2.imwrite(output_path, stego_image)


class DecodeTab(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QHBoxLayout()
        main_layout.addWidget(QLabel("Decode tab"))

        self.setLayout(main_layout)
