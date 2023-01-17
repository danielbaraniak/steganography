import cv2
from PySide6.QtCore import Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QScrollArea, QVBoxLayout, QFileDialog, QGridLayout, QPushButton, \
    QMessageBox


class ImagePreviewWidget(QWidget):
    new_image = Signal(bool)

    def __init__(self):
        super().__init__()
        self.image_path_label = QLabel()
        self.image_path_label.setWordWrap(True)
        self.image_label = QLabel()
        self.image_label.setScaledContents(True)
        self.image_scroll_area = QScrollArea()
        self.image_scroll_area.setWidget(self.image_label)

        self.open_image_button = QPushButton("Open")
        self.open_image_button.clicked.connect(self.open_image)

        layout = QVBoxLayout()

        path_row = QGridLayout()
        path_row.addWidget(QLabel("Path"), 0, 0)
        path_row.addWidget(self.image_path_label, 0, 1)
        path_row.addWidget(self.open_image_button, 0, 2)

        layout.addLayout(path_row)
        layout.addWidget(self.image_scroll_area)

        self.setLayout(layout)

        self.is_loaded = False
        self.cv2_image = None

    def open_image(self):
        file_name = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")

        image = None
        if file_name[0]:
            image = QImage(file_name[0])
            if image.isNull():
                self.is_loaded = False
                self.cv2_image = None
                self.new_image.emit(False)
                return

        self.cv2_image = cv2.imread(file_name[0])

        self.image_label.setPixmap(QPixmap.fromImage(image))
        self.image_label.adjustSize()

        self.image_path_label.setText(file_name[0])

        self.new_image.emit(True)


