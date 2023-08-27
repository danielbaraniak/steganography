from .multi_image_viewer import MultiImageViewer
from ..utils import normalize_for_rgb888, ndarray_to_qimage
from ...core.utils import compute_image_difference


class DifferenceImageViewer(MultiImageViewer):
    def __init__(self, model):
        super().__init__(model, num_images=3)

    def _compute_difference(self) -> None:
        img1 = self.model.get_image(0)
        img2 = self.model.get_image(1)

        if img1 is not None and img2 is not None:
            difference = compute_image_difference(img1, img2)
            normalized_difference = normalize_for_rgb888(difference)
            self._put_image(2, ndarray_to_qimage(normalized_difference))

    def all_views_updated(self):
        self._compute_difference()
