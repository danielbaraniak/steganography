import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QGraphicsView, QHBoxLayout, QGraphicsScene

from stego.gui.utils import ndarray_to_qimage, qimage_to_ndarray


class MultiImageViewer(QWidget):
    ZOOM_IN_FACTOR = 1.25
    ZOOM_OUT_FACTOR = 1 / ZOOM_IN_FACTOR
    image_updated = Signal(int)

    def __init__(self, num_images=2):
        super().__init__()

        self.images: list[np.ndarray | None] = [None for _ in range(num_images)]
        self.views = [QGraphicsView(self) for _ in range(num_images)]
        self.layout = QHBoxLayout()

        for view in self.views:
            self.setup_drag_and_drop(view)
            self.setup_zoom_and_pan(view)
            self.layout.addWidget(view)

        self.setLayout(self.layout)

    def set_image(self, i: int, img_array: np.ndarray) -> None:
        self.images[i] = img_array
        self._update_view(i)
        self.image_updated.emit(i)

    def get_image(self, i: int) -> np.ndarray | None:
        return self.images[i]

    def _update_view(self, i: int) -> None:
        q_img = ndarray_to_qimage(self.images[i])
        self._put_image(i, q_img)

    def _put_image(self, i: int, q_img: QImage) -> None:
        pixmap = QPixmap.fromImage(q_img)
        scene = QGraphicsScene(self)
        scene.addPixmap(pixmap)
        self.views[i].setScene(scene)

    def setup_drag_and_drop(self, view: QGraphicsView) -> None:
        view.setAcceptDrops(True)

        def dragEnterEvent(event):
            if event.mimeData().hasUrls():
                event.acceptProposedAction()

        def dropEvent(event):
            url = event.mimeData().urls()[0]
            image_path = url.toLocalFile()

            q_img = QImage(image_path)
            img_array = qimage_to_ndarray(q_img)
            index = self.views.index(view)

            self.images[index] = img_array
            self._put_image(index, q_img)

            self.image_updated.emit(index)

        view.dragEnterEvent = dragEnterEvent
        view.dropEvent = dropEvent

    def setup_zoom_and_pan(self, view):
        view.wheelEvent = self.zoom_event

        view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        view.horizontalScrollBar().valueChanged.connect(self.sync_horizontal_scroll)
        view.verticalScrollBar().valueChanged.connect(self.sync_vertical_scroll)

    def sync_horizontal_scroll(self, value):
        for view in self.views:
            view.horizontalScrollBar().setValue(value)

    def sync_vertical_scroll(self, value):
        for view in self.views:
            view.verticalScrollBar().setValue(value)

    def zoom_event(self, event):
        factor = (
            self.ZOOM_IN_FACTOR if event.angleDelta().y() > 0 else self.ZOOM_OUT_FACTOR
        )

        for view in self.views:
            view.setTransform(view.transform().scale(factor, factor))
