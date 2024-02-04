import json
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pywt

from stego import config
from stego.core import metrics
from joblib import Parallel, delayed
from tqdm import tqdm


# Image Processing Functions
def compress_image(img, quality=90):
    encode_param = [cv2.IMWRITE_JPEG_QUALITY, quality]
    _, encoded_data = cv2.imencode(".jpg", img, encode_param)
    return cv2.imdecode(encoded_data, cv2.IMREAD_COLOR)


def decompose(
    img: np.ndarray, wavelet: str, max_level: int
) -> list[list[tuple[np.ndarray, ...]]]:
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


# Comparisons


def compare_decompositions(original, compressed, metric, channels) -> dict:
    comparison_results = {}

    for ch_idx, ch in enumerate(channels):
        channel_results = {}
        for level in range(len(original[ch_idx])):
            level_results = {}
            for coeff_name, orig_coeff, comp_coeff in zip(
                ["cA", "cH", "cV", "cD"],
                original[ch_idx][level],
                compressed[ch_idx][level],
            ):
                data_range = (level + 1) * 255
                level_results[coeff_name] = metric(
                    orig_coeff, comp_coeff, data_range=data_range
                )
            channel_results[f"l{level + 1}"] = level_results
        comparison_results[ch] = channel_results
    return comparison_results


def compare(
    original_img: np.ndarray,
    compressed_imgs: list[tuple[int, np.ndarray]],
    wavelet: str,
    max_level: int,
    metric,
    channels,
) -> dict:
    results = {}
    original_decompositions = decompose(original_img, wavelet, max_level)
    for i, (quality, compressed_img) in enumerate(compressed_imgs):
        compressed_decompositions = decompose(compressed_img, wavelet, max_level)
        comparison = compare_decompositions(
            original_decompositions, compressed_decompositions, metric, channels
        )
        results[str(quality)] = comparison
    return results


def compress_and_compare(
    original_img: np.ndarray,
    channels: tuple[str, ...],
    wavelet: str,
    max_level: int,
    qualities: list[int],
    metric,
) -> dict:
    compressed_imgs = [
        (quality, compress_image(original_img, quality)) for quality in qualities
    ]
    return compare(original_img, compressed_imgs, wavelet, max_level, metric, channels)


# Visualization and Saving
def save_results(results: dict, output_dir: str, output_name: str):
    np.save(f"{output_dir}/{output_name}.npy", results)
    with open(f"{output_dir}/{output_name}.json", "w") as f:
        json.dump(results, f)

    with open(f"{output_dir}/{output_name}.json", "r") as f:
        results = json.load(f, parse_float=lambda x: round(float(x), 4))

    with open(f"{output_dir}/{output_name}.json", "w") as f:
        json.dump(results, f)


def plot_channel_data(axes, data, channels, quality_levels, color_pallet):
    for i, quality in enumerate(quality_levels):
        for j, channel in enumerate(channels):
            ax = axes[i, j]
            for coef, color in zip(["cA", "cH", "cV", "cD"], color_pallet):
                plot_data1 = [
                    data[quality][channel][f"l{level}"][coef]["mean_block_threshold_90"]
                    for level in range(1, len(data[quality][channel]) + 1)
                ]
                plot_data2 = [
                    data[quality][channel][f"l{level}"][coef]["pixel_threshold_90"]
                    for level in range(1, len(data[quality][channel]) + 1)
                ]
                ax.plot(
                    range(1, len(data[quality][channel]) + 1),
                    plot_data1,
                    marker="o",
                    label=f"{coef} - block",
                    color=color[0],
                )
                ax.plot(
                    range(1, len(data[quality][channel]) + 1),
                    plot_data2,
                    marker="o",
                    label=f"{coef} - pixel",
                    color=color[1],
                )
                ax.set_title(f"{channel} Channel - Quality {quality}")
                ax.set_xlabel("Level")
                ax.set_ylabel("Mean Difference at 90th percentile")
                ax.legend()
                ax.grid(True)


def create_graph(
    img_path: str | Path, output_dir: str | Path, conversion: int, settings: dict
):
    img_original = cv2.imread(img_path, cv2.IMREAD_COLOR)
    img_to_analyze = cv2.cvtColor(img_original, conversion)

    data = compress_and_compare(img_to_analyze, **settings)
    quality_levels = data.keys()
    fig, axes = plt.subplots(
        nrows=len(quality_levels), ncols=len(settings["channels"]), figsize=(18, 18)
    )

    color_pallet = [
        ("#003366", "#66ccff"),
        ("#006633", "#66ff99"),
        ("#cc0000", "#ff99cc"),
        ("#660066", "#cc99ff"),
    ]

    plot_channel_data(axes, data, settings["channels"], quality_levels, color_pallet)

    img_filename = Path(img_path).stem
    plot_filename = f"{img_filename}_{''.join(settings['channels'])}_mean_diff.png"
    out_path = Path(output_dir) / plot_filename
    plt.savefig(out_path, dpi=600)
    print(f"Saved to {out_path}")


# Main Execution
if __name__ == "__main__":
    output_dir = Path(config.get_output_dir()) / "plots"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    img_dir_path = config.get_images_dir()
    file_names = config.get_images_list()
    img_paths = [img_dir_path + file_name for file_name in file_names]

    conversions = {
        cv2.COLOR_BGR2RGB: ("R", "G", "B"),
        cv2.COLOR_BGR2YCrCb: ("Y", "Cr", "Cb"),
        cv2.COLOR_BGR2HSV: ("H", "S", "V"),
    }

    n_jobs = -1
    color_spaces = [cv2.COLOR_BGR2YCrCb, cv2.COLOR_BGR2RGB, cv2.COLOR_BGR2HSV]
    total_tasks = len(img_paths) * len(color_spaces)

    Parallel(n_jobs=n_jobs, verbose=10)(
        delayed(create_graph)(
            image_path,
            output_dir,
            conversion,
            {
                "qualities": range(50, 100, 15),
                "max_level": 6,
                "wavelet": "haar",
                "metric": metrics.thresholds,
                "channels": conversions[conversion],
            },
        )
        for image_path in tqdm(img_paths, total=total_tasks)
        for conversion in color_spaces
    )
