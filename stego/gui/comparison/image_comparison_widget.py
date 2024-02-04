import pywt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
)

from .color_channel import ColorChannel
from .difference_viewer import DifferenceImageViewer
from .multi_image_model import MultiImageModel


class ImageComparisonWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.model = MultiImageModel()
        self.viewer = DifferenceImageViewer(self.model)

        self.level_selector = QComboBox()
        self.level_selector.addItems([str(i) for i in range(5)])
        self.level_selector.setCurrentIndex(3)
        self.wavelet_selector = QComboBox()
        self.wavelet_selector.addItems(pywt.wavelist(kind="discrete"))
        self.wavelet_selector.setCurrentText("haar")
        self.transform_button = QPushButton("Transform")
        self.transform_button.clicked.connect(self.on_transform_button_clicked)

        self.color_selector = QComboBox()
        self.color_selector.addItems([channel.value for channel in ColorChannel])
        self.color_selector.currentTextChanged.connect(self.on_channel_changed)

        self.detail_selector = QComboBox()
        self.detail_selector.addItems(["ad", "da", "dd"])
        self.detail_selector.currentTextChanged.connect(self.on_detail_changed)

        self.level_view_selector = QComboBox()
        self.level_view_selector.currentTextChanged.connect(self.on_level_changed)

        self.reset_view_button = QPushButton("Reset view")
        self.reset_view_button.clicked.connect(lambda: self.viewer.reset_view())

        self._setup_layout()

    def _setup_layout(self):
        layout = QVBoxLayout()

        transform_layout = QHBoxLayout()
        transform_layout.addWidget(QLabel("Level:"))
        transform_layout.addWidget(self.level_selector)
        transform_layout.addWidget(QLabel("Wavelet:"))
        transform_layout.addWidget(self.wavelet_selector)
        transform_layout.addWidget(self.transform_button)

        view_layout = QHBoxLayout()
        view_layout.addWidget(QLabel("Color:"))
        view_layout.addWidget(self.color_selector)
        view_layout.addWidget(QLabel("Level:"))
        view_layout.addWidget(self.level_view_selector)
        view_layout.addWidget(QLabel("Detail:"))
        view_layout.addWidget(self.detail_selector)
        view_layout.addWidget(self.reset_view_button)

        layout.addLayout(transform_layout)
        layout.addLayout(view_layout)

        layout.addWidget(self.viewer)

        self.setLayout(layout)

    def update_view_level(self, level):
        self.level_view_selector.clear()
        self.level_view_selector.addItems([str(i) for i in range(level + 1)])
        self.level_view_selector.setCurrentIndex(level)

    def on_transform_button_clicked(self):
        settings = {
            "level": int(self.level_selector.currentText()),
            "wavelet": self.wavelet_selector.currentText(),
        }
        self.model.level = 0
        self.model.transform_images(**settings)
        self.update_view_level(settings["level"])

    def on_channel_changed(self, color):
        if color is not None:
            self.model.set_channel(ColorChannel(color))

    def on_detail_changed(self, detail):
        self.model.set_detail(detail)

    def on_level_changed(self, level):
        if level != "":
            self.model.set_level(int(level))
