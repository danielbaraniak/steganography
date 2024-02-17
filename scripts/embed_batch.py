from pathlib import Path
from time import time

import cv2

from scripts import utils
from stego import config
from stego.core import metrics

SECRET = "Lorem ipsum dolor sit"


def embed_batch(size):
    output_dir = Path(config.get_output_dir()) / "test" / f"{size}x{size}"
    Path(output_dir).mkdir(parents=True, exist_ok=True)


    img_dir_path = config.get_images_dir()
    file_names = config.get_images_list()

    encoder_config = config.get_encoder_config()

    measurements = []

    for i, file_name in enumerate(file_names):
        print(file_name)
        img_path = img_dir_path + file_name
        img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)

        if size != img.shape[0]:
            img = utils.resize_image_with_aspect_ratio(img, size)

        original, stego_image, msg_raw = utils.embed(img, SECRET, encoder_config)

        for ext in ["jpg", "png"]:

            info = {"file_name_old": file_name, "file_name_new": f"{i + 1}.{ext}"}

            info |= metrics.diff_metrics(original, stego_image)

            measurements.append(info)

            output_original_path = output_dir / "original" / ext / info["file_name_new"]
            output_stego_path = output_dir / "stego" / ext / info["file_name_new"]

            output_stego_path.parent.mkdir(parents=True, exist_ok=True)
            output_original_path.parent.mkdir(parents=True, exist_ok=True)

            if ext == "jpg":
                cv2.imwrite(
                    str(output_original_path), original, [int(cv2.IMWRITE_JPEG_QUALITY), 100]
                )
                cv2.imwrite(
                    str(output_stego_path), stego_image, [int(cv2.IMWRITE_JPEG_QUALITY), 100]
                )
            else:
                cv2.imwrite(str(output_original_path), original)
                cv2.imwrite(str(output_stego_path), stego_image)

    utils.save_data_to_csv(measurements, str(output_dir / "metadata.csv"))


if __name__ == "__main__":
    start_time = time()
    for size in [1440, 2048, 2448]:
        embed_batch(size)
    end_time = time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time:.2f} seconds")
