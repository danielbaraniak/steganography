from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QGridLayout

from .metrics_widget import MetricsWidget
from .multi_image_viewer import MultiImageViewer
from ..utils import normalize_for_8U, ndarray_to_qimage
from ...core.metrics import get_metrics
from ...core.utils import compute_image_difference


class ComputeMetricsWorker(QThread):
    finished = Signal(dict)

    def __init__(self):
        super().__init__()
        self.img1 = None
        self.img2 = None

    def run(self):
        metrics = get_metrics(self.img1, self.img2)
        self.finished.emit(metrics)

    def set_images(self, img1, img2):
        self.img1 = img1
        self.img2 = img2


class DifferenceImageViewer(MultiImageViewer):
    def __init__(self, model):
        self.metrics_widget = MetricsWidget()
        super().__init__(model, num_images=3)
        self.model.dataChanged.connect(self._compute_difference)


        self.thread = QThread()
        self.worker = ComputeMetricsWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_metrics_thread_finished)

    def initiate_layout(self):
        layout = QGridLayout()
        layout.addWidget(self.views[0], 0, 0)
        layout.addWidget(self.views[1], 0, 1)
        layout.addWidget(self.views[2], 1, 0)
        layout.addWidget(self.metrics_widget, 1, 1)
        self.setLayout(layout)

    def _compute_difference(self) -> None:
        img1 = self.model.get_image(0)
        img2 = self.model.get_image(1)

        if img1 is not None and img2 is not None:
            difference = compute_image_difference(img1, img2)
            normalized_difference = normalize_for_8U(difference)
            self._put_image(2, ndarray_to_qimage(normalized_difference))
            self.start_metrics_thread(img1, img2)

    def start_metrics_thread(self, img1, img2):
        self.worker.set_images(img1, img2)
        self.thread.start()
        self.metrics_widget.loading_indicator.show()

    def on_metrics_thread_finished(self, metrics):
        self.metrics_widget.set_metrics(metrics)
        self.thread.quit()
    def on_model_changed(self, index):
        self._compute_difference()
