import cv2
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QWidget,
    QFileDialog,
    QSlider,
    QMessageBox, QTextEdit,
)

from stego import config
from stego.core.multichannel_coder import encode_color_image
from stego.gui.comparison.image_comparison_widget import ImageComparisonWidget
from stego.gui.encode.image_model import ImageModel
from stego.gui.encode.image_viewer import ImageViewer

IMAGE_FORMATS = config.get_gui_settings().image_formats


class ImageComparisonWidgetWithSave(ImageComparisonWidget):
    def __init__(self, save_callback):
        super().__init__()

        self.reset_view_button.hide()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(save_callback)
        self.layout().addWidget(self.save_button)

    def set_original_image(self, image):
        self.model.set_image(0, image)

    def set_modified_image(self, image):
        self.model.set_image(1, image)


class EncoderWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.model = ImageModel()
        self.image_preview = ImageViewer(self, model=self.model)

        self.comparison_window = ImageComparisonWidgetWithSave(self.save_image_dialog)

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter message here")

        self.alpha_label = QLabel()
        self.alpha_slider = QSlider(self)
        self.alpha_slider.setMinimum(0)
        self.alpha_slider.setMaximum(800)
        self.alpha_slider.setSingleStep(1)
        self.alpha_slider.setOrientation(Qt.Horizontal)
        self.alpha_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.alpha_slider.valueChanged.connect(
            lambda: self.alpha_label.setText(f"{self.alpha_slider.value() / 100:.2f}")
        )
        self.alpha_slider.setValue(100)

        self.embed_button = QPushButton("Embed")
        self.embed_button.clicked.connect(self.embed_message)

        layout = QVBoxLayout()
        layout.addWidget(self.image_preview)
        layout.addWidget(self.message_input)
        layout.addWidget(self.alpha_slider)
        layout.addWidget(self.alpha_label)
        layout.addWidget(self.embed_button)
        self.setLayout(layout)

    def load_image_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Image File", "", IMAGE_FORMATS
        )
        if file_name:
            self.load_image(file_name)

    def save_image_dialog(self):
        if self.model.is_stego_empty():
            QMessageBox.critical(self, "Error", "No image to save.")
            return
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Image File", "", IMAGE_FORMATS
        )
        if file_name:
            cv2.imwrite(
                file_name, cv2.cvtColor(self.model.stego_image, cv2.COLOR_RGB2BGR)
            )

    def load_image(self, path):
        image = cv2.cvtColor(cv2.imread(path, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
        self.model.set_image(image, path)

    def embed_message(self):
        if self.model.is_original_empty():
            QMessageBox.critical(self, "Error", "No image loaded.")
            return

        stego_image = self.create_stego_image()

        self.model.set_stego_image(stego_image)
        self.comparison_window.set_original_image(self.model.image)
        self.comparison_window.set_modified_image(self.model.stego_image)
        self.comparison_window.show()

    def create_stego_image(self):
        default_parameters = config.get_encoder_config()
        custom_parameters = {"alpha": self.alpha_slider.value() / 100}

        encoded_image = encode_color_image(
            self.model.image,
            self.message_input.toPlainText().encode("ASCII", errors="replace"),
            **default_parameters | custom_parameters,
        )

        return encoded_image
