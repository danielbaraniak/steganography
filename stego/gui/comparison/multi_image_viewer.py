from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QGraphicsView, QHBoxLayout, QGraphicsScene

from stego import config
from stego.gui.comparison.multi_image_model import MultiImageModel
from stego.gui.utils import ndarray_to_qimage, qimage_to_ndarray, normalize_for_8U


class MultiImageViewer(QWidget):
    gui_settings = config.get_gui_settings()

    def __init__(self, model: MultiImageModel, num_images=None):
        super().__init__()

        self.model = model
        self.views = [
            QGraphicsView(self) for _ in range(num_images or self.model.rowCount())
        ]

        self.model.dataChanged.connect(self._update_view)

        for view in self.views:
            self.setup_drag_and_drop(view)
            self.setup_zoom_and_scroll(view)

        self.initiate_layout()

    def initiate_layout(self):
        layout = QHBoxLayout()
        for view in self.views:
            layout.addWidget(view)
        self.setLayout(layout)

    def _update_view(self, index) -> None:
        if index == -1:
            for i in range(self.model.rowCount()):
                self._update_view(i)
            return
        img = self.model.get_image(index)
        if img is None:
            return
        q_img = ndarray_to_qimage(normalize_for_8U(img))
        self._put_image(index, q_img)

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

            self.model.set_image(index, img_array)

        view.dragEnterEvent = dragEnterEvent
        view.dropEvent = dropEvent

    def setup_zoom_and_scroll(self, view):
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
        if event.modifiers() & Qt.ControlModifier:
            factor = (
                self.gui_settings.zoom_in_factor
                if event.angleDelta().y() > 0
                else self.gui_settings.zoom_out_factor
            )

            for view in self.views:
                view.setTransform(view.transform().scale(factor, factor))

        elif event.modifiers() & Qt.ShiftModifier:
            for view in self.views:
                view.horizontalScrollBar().setValue(
                    view.horizontalScrollBar().value()
                    - event.angleDelta().y() * self.gui_settings.scroll_step
                )

        else:
            for view in self.views:
                view.verticalScrollBar().setValue(
                    view.verticalScrollBar().value()
                    - event.angleDelta().y() * self.gui_settings.scroll_step
                )

    def reset_view(self):
        for view in self.views:
            view.setScene(None)
