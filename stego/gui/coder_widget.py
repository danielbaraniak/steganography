from os import path

import cv2
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFileDialog, QPushButton, QVBoxLayout, QMessageBox, \
    QGridLayout, QSlider, QLineEdit

from stego.coder.image_coder import RobustStegoCoder
from stego.coder.message import MessageNotFoundException
from stego.coder.transform.dwt import Dwt
from stego.gui.image_preview import ImagePreviewWidget


class CoderWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.image_preview_widget = ImagePreviewWidget()
        self.image_preview_widget.new_image.connect(self.new_image_handler)

        self.compression_quality_slider = QSlider(self)
        self.compression_quality_label = QLabel()
        self.message_field = QLineEdit()

        self.encode_button = QPushButton("Encode")
        self.encode_button.clicked.connect(self.encode)
        self.encode_button.setEnabled(False)

        self.decode_button = QPushButton("Decode")
        self.decode_button.clicked.connect(self.decode)
        self.decode_button.setEnabled(False)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_preview_widget)
        main_layout.addLayout(self.create_coder_controls())

        self.setLayout(main_layout)

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

        encoder_info = [
            ("Compression quality", self.compression_quality_slider, self.compression_quality_label),
            ("Message", self.message_field, QLabel("\t")),
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

    def new_image_handler(self, is_loaded):
        print(is_loaded)
        if is_loaded:
            self.encode_button.setEnabled(True)
            self.decode_button.setEnabled(True)
        else:
            self.encode_button.setEnabled(False)
            self.decode_button.setEnabled(False)

    def decode(self):
        print("in decode")
        stego_coder = RobustStegoCoder(
            Dwt('haar', level=3),
            levels_to_encode=1,
            alpha=1
        )

        image = self.image_preview_widget.cv2_image
        try:
            message = stego_coder.decode_color_image(image)
            print(message)
            if message:
                QMessageBox.information(self, "Hidden Message", str(message))
            else:
                QMessageBox.warning(self, "Decoding Error", f"Cannot find a message.")
        except MessageNotFoundException:
            QMessageBox.warning(self, "Decoding Error", f"Cannot find a message.")

    def encode(self):
        compression_quality = self.compression_quality_slider.value()
        message = self.message_field.text()

        output_path = QFileDialog.getSaveFileName(
            self, "Save Image", "", "Image Files (*.jpg)")

        if output_path[0]:
            output_path = output_path[0]

            filename, file_extension = path.splitext(output_path)
            if not file_extension:
                output_path = filename + ".jpg"
        else:
            return

        image = self.image_preview_widget.cv2_image
        stego_coder = RobustStegoCoder(
            Dwt('haar', level=3),
            levels_to_encode=1,
            quality_level=compression_quality,
            alpha=1
        )
        stego_image = stego_coder.encode_color_image(image, message)

        cv2.imwrite(output_path, stego_image)

