from PySide6.QtWidgets import QGridLayout

from .metrics_widget import MetricsWidget
from .multi_image_viewer import MultiImageViewer
from ..utils import normalize_for_8U, ndarray_to_qimage
from ...core.metrics import get_metrics
from ...core.utils import compute_image_difference


class DifferenceImageViewer(MultiImageViewer):
    def __init__(self, model):
        self.metrics_widget = MetricsWidget()
        super().__init__(model, num_images=3)
        self.model.dataChanged.connect(self._compute_difference)
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

            metrics = get_metrics(img1, img2)
            self.metrics_widget.set_metrics(metrics)

    def on_model_changed(self, index):
        self._compute_difference()
