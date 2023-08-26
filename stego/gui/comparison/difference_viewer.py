import numpy as np

from .multi_image_viewer import MultiImageViewer
from ..utils import normalize_for_rgb888
from ...core.utils import compute_image_difference


class DifferenceImageViewer(MultiImageViewer):
    def __init__(self):
        super().__init__(num_images=3)

        self.image_updated.connect(self._on_image_updated)

    def set_image1(self, img_array: np.ndarray) -> None:
        super().set_image(0, img_array)

    def set_image2(self, img_array: np.ndarray) -> None:
        super().set_image(1, img_array)

    def _compute_difference(self) -> None:
        img1 = super().get_image(0)
        img2 = super().get_image(1)

        if img1 is not None and img2 is not None:
            difference = compute_image_difference(img1, img2)
            difference = normalize_for_rgb888(difference)
            super().set_image(2, difference)

    def _on_image_updated(self, index: int) -> None:
        if index in [0, 1]:
            self._compute_difference()
