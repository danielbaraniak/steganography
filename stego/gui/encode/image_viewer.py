from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PySide6.QtWidgets import QWidget, QGraphicsView, QLabel, QPushButton, QVBoxLayout, QGraphicsScene, QHBoxLayout

from stego import config
from stego.gui.encode.image_model import ImageModel
from stego.gui.utils import normalize_for_8U, ndarray_to_qimage


class ImageViewer(QWidget):
    gui_settings = config.get_gui_settings()

    def __init__(self, parent, model):
        super().__init__(parent)
        self.model: ImageModel = model
        self.view = QGraphicsView(self)
        self.setup_view()

        self.image_path_label = QLabel()
        self.image_path_label.setWordWrap(True)

        self.load_image_button = QPushButton("Load")
        self.load_image_button.clicked.connect(self.parent().load_image_dialog)
        self.model.image_original_updated.connect(self.on_image_updated)

        layout = QVBoxLayout()

        first_line = QHBoxLayout()
        first_line.addWidget(self.image_path_label)
        first_line.addWidget(self.load_image_button)
        first_line.setStretch(0, 1)

        layout.addLayout(first_line)
        layout.addWidget(self.view)
        self.setLayout(layout)

    def on_image_updated(self):
        self.image_path_label.setText(self.model.path)
        self.image_path_label.adjustSize()

        q_img = ndarray_to_qimage(normalize_for_8U(self.model.image))
        pixmap = QPixmap.fromImage(q_img)
        scene = QGraphicsScene(self.view)
        scene.addPixmap(pixmap)
        self.view.setScene(scene)

    def setup_view(self):
        self.view.acceptDrops()

        def dragEnterEvent(event: QDragEnterEvent) -> None:
            if event.mimeData().hasUrls():
                event.acceptProposedAction()

        def dropEvent(event: QDropEvent) -> None:
            url = event.mimeData().urls()[0]
            image_path = url.toLocalFile()
            self.parent().load_image(image_path)

        self.view.dropEvent = dropEvent
        self.view.dragEnterEvent = dragEnterEvent

        self.view.wheelEvent = self.zoom_event

    def zoom_event(self, event):
        if event.modifiers() & Qt.ControlModifier:

            factor = (
                self.gui_settings.zoom_in_factor if event.angleDelta().y() > 0 else self.gui_settings.zoom_out_factor
            )

            self.view.scale(factor, factor)

        elif event.modifiers() & Qt.ShiftModifier:
            self.view.horizontalScrollBar().setValue(
                self.view.horizontalScrollBar().value() - event.angleDelta().y() * self.gui_settings.scroll_step
            )

        else:
            self.view.verticalScrollBar().setValue(
                self.view.verticalScrollBar().value() - event.angleDelta().y() * self.gui_settings.scroll_step
            )
