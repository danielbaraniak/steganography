import cv2
import numpy as np
from skimage import metrics

from stego.core import blocking
from stego.core.utils import match_sizes


def get_metrics(img1, img2):
    stats = {
        "img1": {
            "min": np.min(img1),
            "max": np.max(img1),
            "shape": img1.shape[:2],
        },
        "img2": {
            "min": np.min(img2),
            "max": np.max(img2),
            "shape": img2.shape[:2],
        },
        "diff": diff_metrics(img1, img2),
    }

    return stats


def diff_metrics(img1, img2):
    img1, img2 = match_sizes(img1, img2)
    difference = img1 - img2
    is_grayscale = img1.ndim == 2
    data_range = max(np.max(img1), np.max(img2)) - min(np.min(img1), np.min(img2))

    diff = {
        "min": np.min(difference),
        "max": np.max(difference),
        "abs_diff_mean": np.mean(np.abs(difference)),
        "psnr": metrics.peak_signal_noise_ratio(img1, img2, data_range=data_range),
        "ssim": metrics.structural_similarity(img1, img2, data_range=data_range,
                                              channel_axis=None if is_grayscale else 2),
        "mse": metrics.mean_squared_error(img1, img2)
    }
    return diff


def psnr(img1, img2, data_range):
    return {"psnr": metrics.peak_signal_noise_ratio(img1, img2, data_range=data_range)}


def mean_diff(img1, img2, **kwargs):
    return {"mean_diff": np.mean(img1) - np.mean(img2)}


def thresholds(original, compressed, data_range=255):
    block_size = 3
    diff = cv2.absdiff(original, compressed) / 255
    diff_blocks = blocking.divide_image(diff, block_size)
    return {
        "mean_block_threshold_90": np.quantile(np.abs(np.mean(diff_blocks, axis=(1, 2))), 0.9),
        "pixel_threshold_90": np.quantile(np.abs(diff), 0.9)
    }
