import cv2
import numpy as np
from skimage import metrics

from stego.core.utils import match_sizes


def get_metrics(img1, img2):
    stats = {
        "img1": {
            "min": np.min(img1),
            "max": np.max(img1),
            "std": np.std(img1),
        },
        "img2": {
            "min": np.min(img2),
            "max": np.max(img2),
            "std": np.std(img2),
        },
        "diff": diff_metrics(img1, img2),
    }

    return stats


def diff_metrics(img1, img2):
    img1, img2 = match_sizes(img1, img2)
    difference = cv2.absdiff(img1, img2)
    is_grayscale = img1.ndim == 2
    data_range = max(np.max(img1), np.max(img2)) - min(np.min(img1), np.min(img2))

    diff = {
        "min": np.min(difference),
        "max": np.max(difference),
        "std": np.std(difference),
        "mean": np.mean(difference),
        "psnr": metrics.peak_signal_noise_ratio(img1, img2, data_range=data_range),
        "ssim": metrics.structural_similarity(img1, img2, data_range=data_range, channel_axis=None if is_grayscale else 2),
        "mse": metrics.mean_squared_error(img1, img2)
    }
    return diff