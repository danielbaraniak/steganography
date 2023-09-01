import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pywt
from skimage.metrics import peak_signal_noise_ratio


def psnr(img1, img2):
    data_range = max(np.max(img1), np.max(img2)) - min(np.min(img1), np.min(img2))

    diff = {
        "psnr": peak_signal_noise_ratio(img1, img2, data_range=data_range),

    }
    return diff


def compress_image(img, quality=90):
    encode_param = [cv2.IMWRITE_JPEG_QUALITY, quality]
    _, encoded_data = cv2.imencode('.jpg', img, encode_param)
    return cv2.imdecode(encoded_data, cv2.IMREAD_COLOR)


def decompose(img: np.ndarray, wavelet: str, max_level: int) -> list[
    list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]]:
    decompositions = []
    for ch in range(img.shape[2]):
        channel = img[:, :, ch]
        coeffs = []
        for _ in range(max_level):
            cA, (cH, cV, cD) = pywt.dwt2(channel, wavelet)
            coeffs.append((cA, cH, cV, cD))
            channel = cA
        decompositions.append(coeffs)
    return decompositions


def compare_decompositions(original: list[list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]],
                           compressed: list[list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]],
                           metric, channels) -> dict:
    comparison_results = {}

    for ch_idx, ch in enumerate(channels):
        channel_results = {}

        for level in range(len(original[ch_idx])):
            level_results = {}

            for coeff_name, orig_coeff, comp_coeff in zip(['cA', 'cH', 'cV', 'cD'], original[ch_idx][level],
                                                          compressed[ch_idx][level]):
                level_results[coeff_name] = metric(orig_coeff, comp_coeff)

            channel_results[f"l{level + 1}"] = level_results
        comparison_results[ch] = channel_results

    return comparison_results


def compare(original_img: np.ndarray, compressed_imgs: list[tuple[int, np.ndarray]], wavelet: str, max_level: int,
            metric, channels) -> dict:
    results = {}
    original_decompositions = decompose(original_img, wavelet, max_level)
    for i, (quality, compressed_img) in enumerate(compressed_imgs):
        compressed_decompositions = decompose(compressed_img, wavelet, max_level)
        comparison = compare_decompositions(original_decompositions, compressed_decompositions, metric, channels)
        results[f"{quality}"] = comparison
    return results


def compress_and_compare(original_img_path: str, wavelet: str, max_level: int, qualities: list[int],
                         metric) -> dict:
    original_img = cv2.cvtColor(cv2.imread(original_img_path), cv2.COLOR_BGR2YCrCb)
    channels = ['Y', 'Cr', 'Cb']
    compressed_imgs = [(quality, compress_image(original_img, quality)) for quality in qualities]
    results = compare(original_img, compressed_imgs, wavelet, max_level, metric, channels)
    return results


def mean_diff(img1, img2):
    diff = {
        "mean_diff": np.mean(img1) - np.mean(img2)
    }
    return diff


def run_and_save(img, output_dir, output_name, **params):
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    results = compress_and_compare(img, **params)

    np.save(f"{output_dir}/{output_name}.npy", results)
    with open(f"{output_dir}/{output_name}.json", "w") as f:
        json.dump(results, f)

    with open(f"{output_dir}/{output_name}.json", "r") as f:
        results = json.load(f, parse_float=lambda x: round(float(x), 4))

    with open(f"{output_dir}/{output_name}.json", "w") as f:
        json.dump(results, f)


if __name__ == '__main__':
    input_path = sys.argv[1]
    output_dir = "./metrics"
    output_name = Path(input_path).name.split('.')[0]
    params = {
        "wavelet": "haar",
        "max_level": 5,
        "qualities": [40, 60, 70, 80, 90, 100],
        "metric": mean_diff
    }

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    img = cv2.cvtColor(cv2.imread(input_path), cv2.COLOR_BGR2RGB)
    run_and_save(img, output_dir, output_name, **params)
