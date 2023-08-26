import numpy as np

from .multi_image_viewer import MultiImageViewer
from ...core.utils import compute_image_difference


def normalize_for_rgb888(img: np.ndarray) -> np.ndarray:
    is_grayscale = img.ndim == 2
    is_rgb888 = img.ndim == 3 and img.shape[2] == 3

    if is_grayscale:
        img = np.stack([img] * 3, axis=-1)
    elif not is_rgb888:
        raise ValueError("Image must be grayscale or RGB888.")

    range_size = np.max(img) - np.min(img)

    if range_size == 0:
        normalized_array = img
    else:
        normalized_array = ((img - np.min(img)) * (255 / range_size)).astype(np.uint8)

    return normalized_array


class DifferenceImageViewer(MultiImageViewer):
    def __init__(self):
        super().__init__(num_images=3)

        self.image_updated.connect(self._on_image_updated)

    def set_image1(self, img_array: np.ndarray) -> None:
        super().set_image_at_index(0, img_array)

    def set_image2(self, img_array: np.ndarray) -> None:
        super().set_image_at_index(1, img_array)

    def _compute_difference(self) -> None:
        img1 = super().get_image_at_index(0)
        img2 = super().get_image_at_index(1)

        if img1 is not None and img2 is not None:
            difference = compute_image_difference(img1, img2)
            difference = normalize_for_rgb888(difference)
            super().set_image_at_index(2, difference)

    def _on_image_updated(self, index: int) -> None:
        if index in [0, 1]:
            self._compute_difference()
