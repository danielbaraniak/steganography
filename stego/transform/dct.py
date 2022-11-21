import cv2
import numpy as np


def dct(src: np.ndarray) -> np.ndarray:
    return cv2.dct(np.float32(src) - 127)


def idct(src: np.ndarray) -> np.ndarray:
    return np.uint8(cv2.idct(src) + 127)
