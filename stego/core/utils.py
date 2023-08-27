import cv2
import numpy as np
import pywt


def compute_image_difference(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    if img1.shape != img2.shape:
        raise ValueError("Both images must have the same shape.")

    return np.abs(img1 - img2)


def dwt_rgb_forward(img: np.ndarray, *args, **kwargs):
    return [pywt.wavedecn(channel, *args, **kwargs) for channel in cv2.split(img)]
