import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QGraphicsView, QHBoxLayout, QGraphicsScene


class MultiImageViewer(QWidget):
    ZOOM_IN_FACTOR = 1.25
    image_updated = Signal(int)

    def __init__(self, num_images=2):
        super().__init__()

        self.views = [QGraphicsView(self) for _ in range(num_images)]

        self.layout = QHBoxLayout()

        for view in self.views:
            self.setup_drag_and_drop(view)
            self.setup_zoom_and_pan(view)

            self.layout.addWidget(view)

        self.setLayout(self.layout)

    def set_image_at_index(self, i: int, img_array: np.ndarray) -> None:
        """
        Set image at the specified index using a NumPy array.
        :param i: Index of the view
        :param img_array: Image as a NumPy array (RGB888)
        """

        height, width, channel = img_array.shape
        bytes_per_line = channel * width
        q_img = QImage(img_array.data, width, height, bytes_per_line, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(q_img)
        scene = QGraphicsScene(self)
        scene.addPixmap(pixmap)
        self.views[i].setScene(scene)

        self.image_updated.emit(i)

    def get_image_at_index(self, i: int) -> np.ndarray | None:
        """
        Get the image at the specified index as a NumPy array.
        :param i: Index of the view
        :return: Image as a NumPy array (RGB888)
        """

        scene = self.views[i].scene()
        if scene is None or len(scene.items()) == 0:
            return None
        pixmap = scene.items()[0].pixmap()
        q_img = pixmap.toImage().convertToFormat(QImage.Format_RGBA8888)

        img_array = (np.array(q_img.constBits()).reshape((q_img.height(), q_img.width(), 4))).astype(np.uint8)

        return img_array[:, :, :3]

    def load_image(self, view, image_path):
        image = QImage(image_path)
        pixmap = QPixmap.fromImage(image)
        scene = QGraphicsScene(self)
        scene.addPixmap(pixmap)
        view.setScene(scene)

    def setup_drag_and_drop(self, view):
        view.setAcceptDrops(True)

        def dragEnterEvent(event):
            if event.mimeData().hasUrls():
                event.acceptProposedAction()

        def dropEvent(event):
            url = event.mimeData().urls()[0]
            image_path = url.toLocalFile()
            self.load_image(view, image_path)
            self.image_updated.emit(self.views.index(view))

        view.dragEnterEvent = dragEnterEvent
        view.dropEvent = dropEvent

    def setup_zoom_and_pan(self, view):
        view.wheelEvent = self.zoom_event

        # Ensure scroll bars are always visible
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # Connect scroll bar signals to synchronize scrolling
        view.horizontalScrollBar().valueChanged.connect(self.sync_horizontal_scroll)
        view.verticalScrollBar().valueChanged.connect(self.sync_vertical_scroll)

    def sync_horizontal_scroll(self, value):
        for view in self.views:
            view.horizontalScrollBar().setValue(value)

    def sync_vertical_scroll(self, value):
        for view in self.views:
            view.verticalScrollBar().setValue(value)

    def zoom_event(self, event):
        zoom_out_factor = 1 / self.ZOOM_IN_FACTOR
        factor = self.ZOOM_IN_FACTOR if event.angleDelta().y() > 0 else zoom_out_factor

        for view in self.views:
            view.setTransform(view.transform().scale(factor, factor))
