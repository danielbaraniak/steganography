import numpy as np


def compute_image_difference(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    if img1.shape != img2.shape:
        raise ValueError("Both images must have the same shape.")

    return np.abs(img1 - img2)
