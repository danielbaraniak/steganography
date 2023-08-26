import numpy as np
from PySide6.QtGui import QImage


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


def qimage_to_ndarray(q_img: QImage) -> np.ndarray:
    q_img = q_img.convertToFormat(QImage.Format_RGBA8888)
    img_array = (
        np.array(q_img.constBits())
        .astype(np.uint8)
        .reshape((q_img.height(), q_img.width(), 4))
    )
    return img_array[:, :, :3]


def ndarray_to_qimage(img_array: np.ndarray) -> QImage:
    height, width, channel = img_array.shape
    bytes_per_line = channel * width
    q_img = QImage(img_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
    return q_img
