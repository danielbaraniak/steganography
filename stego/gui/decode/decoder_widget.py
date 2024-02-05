import cv2
from PySide6.QtWidgets import (
    QTextBrowser,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QFileDialog,
    QMessageBox,
)

from stego import config
from stego.core.multichannel_coder import decode_color_image
from stego.gui.encode.image_model import ImageModel
from stego.gui.encode.image_viewer import ImageViewer

IMAGE_FORMATS = config.get_gui_settings().image_formats


class DecoderWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.model = ImageModel()
        self.image_preview = ImageViewer(self, model=self.model)

        self.message_display = QTextBrowser()
        self.message_display.setPlaceholderText("Decoded message will appear here")

        self.decode_button = QPushButton("Decode")
        self.decode_button.clicked.connect(self.decode_message)

        layout = QVBoxLayout()
        layout.addWidget(self.image_preview)
        layout.addWidget(self.decode_button)
        layout.addWidget(self.message_display)
        self.setLayout(layout)

    def load_image_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Image File", "", IMAGE_FORMATS
        )
        if file_name:
            self.load_image(file_name)

    def load_image(self, path):
        image = cv2.cvtColor(cv2.imread(path, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
        self.model.set_image(image, path)

    def decode_message(self):
        if self.model.is_original_empty():
            QMessageBox.critical(self, "Error", "No image loaded.")
            return

        decoded_message = self.get_decoded_message()

        self.message_display.setText(decoded_message)

    def get_decoded_message(self):
        default_parameters = config.get_encoder_config()

        decoded_message_bytes, ecc_message, _ = decode_color_image(
            self.model.image, **default_parameters
        )

        if not decoded_message_bytes:
            return "No message found. Closest result: " + ecc_message.decode(
                "ASCII", errors="replace"
            )
        else:
            return decoded_message_bytes.decode("ASCII", errors="replace")
