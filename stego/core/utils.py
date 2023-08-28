import logging

import cv2
import numpy as np
import pywt


def compute_image_difference(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    img1, img2 = match_sizes(img1, img2)

    return cv2.absdiff(img1, img2)


def dwt_rgb_forward(img: np.ndarray, *args, **kwargs):
    return [pywt.wavedecn(channel, *args, **kwargs) for channel in cv2.split(img)]


def match_sizes(img1: np.ndarray, img2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if img1.shape != img2.shape:
        logging.warning("Images have different shapes")
        img1_height, img1_width = img1.shape[:2]
        img2 = cv2.resize(img2, (img1_width, img1_height), interpolation=cv2.INTER_LANCZOS4)
    return img1, img2
