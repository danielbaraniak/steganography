from pathlib import Path
from time import time

import cv2

from scripts import utils
from stego import config
from stego.core import metrics


def decode_batch(size):
    output_dir = Path(config.get_output_dir()) / "test" / f"{size}x{size}"
    output_dir.mkdir(parents=True, exist_ok=True)

    processed_dir_path = output_dir / "processed"
    stego_dir_path = output_dir / "stego"
    encoder_config = config.get_encoder_config()

    file_names = [f.name for f in processed_dir_path.iterdir() if f.is_file()]

    results = []

    for file_name in file_names:
        print(file_name)

        stego_img_path = stego_dir_path / file_name
        processed_img_path = processed_dir_path / file_name

        stego_img = cv2.imread(str(stego_img_path), cv2.IMREAD_COLOR)
        processed_img = cv2.imread(str(processed_img_path), cv2.IMREAD_COLOR)

        # processed_img = utils.resize_image_with_aspect_ratio(processed_img, 2016)

        message, message_parts = utils.decode(processed_img, encoder_config)
        print(message)

        result = {"file_name": file_name, "message": message}

        info = metrics.diff_metrics(stego_img, processed_img)
        result |= info

        results.append(result)

    utils.save_data_to_csv(results, str(output_dir / "decoding_results.csv"))


if __name__ == "__main__":
    start_time = time()
    decode_batch(2448)
    end_time = time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time:.2f} seconds")