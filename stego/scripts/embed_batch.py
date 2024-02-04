import csv
import itertools
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from time import time

import cv2
import numpy as np
from pqdm.processes import pqdm

from stego import config
from stego.core import metrics
from stego.core import multichannel_coder
from stego.core.errors import CapacityError

SECRET = "Lorem ipsum dolor sit amet"


def resize_image_with_aspect_ratio(img, new_width: int):
    original_width = img.shape[1]
    original_height = img.shape[0]
    aspect_ratio = original_height / original_width
    new_height = int(new_width * aspect_ratio)

    resized_image = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

    return resized_image


def embed(img, message, parameters):
    img_original = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    original, stego_image, msg_parts = multichannel_coder.encode_color_image(img_original,
                                                                             message.encode("ASCII", errors="replace"),
                                                                             **parameters)

    return cv2.cvtColor(original, cv2.COLOR_RGB2BGR), cv2.cvtColor(stego_image, cv2.COLOR_RGB2BGR), msg_parts


def save_data_to_csv(data: list[dict], filename: str):
    with open(filename, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys(), extrasaction='ignore', delimiter=";", dialect='excel')
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f"Content saved to {filename}")


def decode(img, parameters):
    message, message_parts = multichannel_coder.decode_color_image(img, **parameters)
    if message is not None: message = message.decode("ASCII", errors="replace")

    return message, message_parts


def compress_image(image, quality):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    result, encimg = cv2.imencode('.jpg', image, encode_param)
    if not result:
        raise Exception("Could not compress image")
    image = cv2.imdecode(encimg, 1)
    return image


def embed_batch():
    output_dir = Path(config.get_output_dir()) / "test"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path(output_dir / "original").mkdir(parents=True, exist_ok=True)
    Path(output_dir / "stego").mkdir(parents=True, exist_ok=True)

    img_dir_path = config.get_images_dir()
    file_names = config.get_images_list()

    encoder_config = config.get_encoder_config()

    measurements = []

    for i, file_name in enumerate(file_names):
        print(file_name)
        img_path = img_dir_path + file_name
        img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
        # img = resize_image_with_aspect_ratio(img, 1440)
        original, stego_image, msg_parts = embed(img, SECRET, encoder_config)

        file_meta = {
            "file_name_old": file_name,
            "file_name_new": f"{i + 1}.jpg"
        }

        info = metrics.diff_metrics(original, stego_image)

        info |= file_meta
        measurements.append(info)

        output_original_path = output_dir / "original" / file_meta["file_name_new"]
        output_stego_path = output_dir / "stego" / file_meta["file_name_new"]

        cv2.imwrite(str(output_original_path), original, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        cv2.imwrite(str(output_stego_path), stego_image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

    save_data_to_csv(measurements, str(output_dir / "metadata.csv"))


def decode_batch():
    output_dir = Path(config.get_output_dir()) / "test"
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

        # processed_img = resize_image_with_aspect_ratio(processed_img, 2448)

        processed_img = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB)
        message, message_parts = decode(processed_img, encoder_config)

        result = {"file_name": file_name, "message": message}

        # info = metrics.diff_metrics(stego_img, processed_img)
        # result |= info

        results.append(result)

    save_data_to_csv(results, str(output_dir / "decoding_results.csv"))


def calculate_accuracy(payload1, payload2):
    matching_bits = 0
    total_bits = 0

    payload1 = itertools.cycle(payload1)

    for p_original, p_retrieved in zip(payload1, payload2):
        arr_original = np.frombuffer(p_original, dtype=np.uint8)
        arr_retrieved = np.frombuffer(p_retrieved, dtype=np.uint8)

        arr_retrieved = arr_retrieved[:arr_original.size]

        # Convert bytes to bits
        arr_original_bits = np.unpackbits(arr_original)
        arr_retrieved_bits = np.unpackbits(arr_retrieved)

        # Compare bits
        matching_bits += np.sum(arr_original_bits == arr_retrieved_bits)
        total_bits += arr_original_bits.size

    return matching_bits / total_bits


def encode_compress_decode(encoder_config, img_dir_path, file_name):
    img_path = img_dir_path + file_name
    img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)

    info = defaultdict(int)
    info["file_name"] = file_name
    info |= encoder_config
    try:
        original, stego_image, msg_parts = embed(img, SECRET, encoder_config)
    except CapacityError:
        return info

    decoded_results = {}
    for quality in range(75, 50, -10):
        compressed_image = compress_image(stego_image, quality)
        message, message_parts_decoded = decode(compressed_image, encoder_config)
        correct_bits = calculate_accuracy(msg_parts, message_parts_decoded)
        decoded_results[f"{quality}_correct_bits"] = correct_bits
        decoded_results[f"{quality}_is_success"] = message == SECRET

    info |= metrics.diff_metrics(original, stego_image)

    info |= decoded_results

    return info


def main():
    encoder_config = config.get_encoder_config()

    output_dir = Path(config.get_output_dir()) / "test"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    img_dir_path = config.get_images_dir()
    file_names = config.get_images_list()

    args = []

    for ecc_symbols, level, block_size, use_channels, file_name in itertools.product([0, 5, 10, 15],
                                                                                     [3, 4, 5],
                                                                                     [3, 5],
                                                                                     [[0], [1], [2], [1, 2]],
                                                                                     file_names):
        custom_config = {"ecc_symbols": ecc_symbols,
                         "level": level,
                         "block_size": block_size,
                         "use_channels": use_channels,
                         }

        parameters = encoder_config.copy()
        parameters |= custom_config
        args.append([parameters, img_dir_path, file_name])

    # for ecc_symbols, level, file_name in itertools.product([0, 5],  [3, 4],file_names):
    #     custom_config = {"ecc_symbols": ecc_symbols,
    #                      "level": level,
    #                      }
    #
    #     parameters = encoder_config.copy()
    #     parameters |= custom_config
    #     args.append([parameters, img_dir_path, file_name])

    results = pqdm(args, encode_compress_decode, n_jobs=7, argument_type='args')

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_data_to_csv(results, str(output_dir / f"encode_modify_decode_{timestamp}.csv"))


if __name__ == '__main__':
    start_time = time()
    main()
    end_time = time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time:.2f} seconds")