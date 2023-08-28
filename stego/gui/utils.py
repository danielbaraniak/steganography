import cv2
import numpy as np
from PySide6.QtGui import QImage


def normalize_for_8U(img: np.ndarray) -> np.ndarray:
    is_grayscale = img.ndim == 2
    is_rgb = img.ndim == 3 and img.shape[2] == 3

    if not (is_grayscale or is_rgb):
        raise ValueError("Image must be grayscale or RGB.")

    normalized_img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    return normalized_img


def qimage_to_ndarray(q_img: QImage) -> np.ndarray:
    q_img = q_img.convertToFormat(QImage.Format_RGBA8888)
    img_array = (
        np.array(q_img.constBits())
        .astype(np.uint8)
        .reshape((q_img.height(), q_img.width(), 4))
    )
    return img_array[:, :, :3]


def ndarray_to_qimage(img_array: np.ndarray) -> QImage:
    match img_array.ndim:
        case 2:
            height, width = img_array.shape
            bytes_per_line = width
            img_format = QImage.Format_Grayscale8
        case _:
            height, width, channel = img_array.shape
            bytes_per_line = channel * width
            img_format = QImage.Format_RGB888

    q_img = QImage(img_array.data, width, height, bytes_per_line, img_format)
    return q_img
