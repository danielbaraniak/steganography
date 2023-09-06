from PySide6.QtCore import Signal, QObject


class ImageModel(QObject):
    image_original_updated = Signal()
    image_stego_updated = Signal()

    def __init__(self):
        super().__init__()
        self.image = None
        self.stego_image = None
        self.path = None

    def set_image(self, image, path):
        self.image = image
        self.path = path
        self.image_original_updated.emit()

    def set_stego_image(self, image):
        self.stego_image = image
        self.image_stego_updated.emit()

    def is_original_empty(self):
        return self.image is None

    def is_stego_empty(self):
        return self.stego_image is None


