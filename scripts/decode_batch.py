from pathlib import Path
from time import time

import cv2

from scripts import utils
from scripts.embed_batch import SECRET
from stego import config
from stego.core import message as msg_utils
from skimage import metrics


names_mapping = {
    "1.jpg": "baloons",
    "2.jpg": "billiard_balls_b",
    "3.jpg": "cards_b",
    "4.jpg": "cushions",
    "5.jpg": "garden_table",
    "6.jpg": "pillar",
    "7.jpg": "scarf",
    "8.jpg": "sweets",
    "9.jpg": "tools_b",
}


def decode_batch(size, file_size):
    output_dir = Path(config.get_output_dir()) / "test_platforms" / f"{size}x{size}"

    encoder_config = config.get_encoder_config()

    results = []

    for platform in ["facebook", "instagram"]:
        processed_dir_path = output_dir / platform
        stego_dir_path = output_dir / "stego" / "jpg"

        file_names = [f.name for f in processed_dir_path.iterdir() if f.is_file()]

        for file_name in file_names:
            print(file_name)

            processed_img_path = processed_dir_path / file_name
            stego_img_path = stego_dir_path / file_name

            processed_img = cv2.imread(str(processed_img_path), cv2.IMREAD_COLOR)
            stego_img = cv2.imread(str(stego_img_path), cv2.IMREAD_COLOR)

            matched_size_processed = utils.resize_image_with_aspect_ratio(
                processed_img, file_size
            )
            psnr = metrics.peak_signal_noise_ratio(stego_img, matched_size_processed)

            message, ecc_message, message_raw = utils.decode(
                processed_img, encoder_config
            )
            print(message)

            ecc_message_original = msg_utils.encode_ecc(
                SECRET.encode("ASCII"), **encoder_config
            )
            correct_bytes_count = sum(
                1
                for msg, msg_decoded in zip(ecc_message_original, ecc_message)
                if msg == msg_decoded
            )
            result = {
                "processed_dir": processed_dir_path,
                "image_name": names_mapping[file_name],
                "is_success": message == SECRET,
                "correct_bytes": correct_bytes_count / len(ecc_message_original),
                "platform": platform,
                "size": processed_img.shape[0],
                "size_original": size,
                "psnr": psnr,
                "resized": False,
            }

            results.append(result)

    return results


if __name__ == "__main__":
    start_time = time()
    results = []
    for size in [(1440, 1440), (2048, 2040), (2448, 2440)]:
        results += decode_batch(*size)

    utils.save_data_to_csv(
        results,
        Path(config.get_output_dir()) / "test_platforms" / "decoding_results.csv",
    )
    end_time = time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time:.2f} seconds")
