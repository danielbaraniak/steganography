import csv
import itertools

import cv2
import numpy as np

from stego.core import multichannel_coder


def resize_image_with_aspect_ratio(img, new_width: int):
    original_width = img.shape[1]
    original_height = img.shape[0]
    aspect_ratio = original_height / original_width
    new_height = int(new_width * aspect_ratio)

    if original_width == new_width and original_height == new_height:
        return img

    resized_image = cv2.resize(
        img, (new_width, new_height), interpolation=cv2.INTER_CUBIC
    )

    return resized_image


def embed(img, message, parameters):
    img_original = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    original, stego_image, msg_raw = multichannel_coder.encode_color_image(
        img_original, message.encode("ASCII", errors="replace"), **parameters
    )

    return (
        cv2.cvtColor(original, cv2.COLOR_RGB2BGR),
        cv2.cvtColor(stego_image, cv2.COLOR_RGB2BGR),
        msg_raw,
    )


def save_data_to_csv(data: list[dict], filename: str):
    with open(filename, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=data[0].keys(),
            extrasaction="ignore",
            delimiter=";",
            dialect="excel",
        )
        writer.writeheader()
        for row in data:
            try:
                writer.writerow(row)
            except:
                print(row)

    print(f"Content saved to {filename}")


def decode(img, parameters):
    message, ecc_message, message_raw = multichannel_coder.decode_color_image(
        img, **parameters
    )
    if message is not None:
        message = message.decode("ASCII", errors="replace")

    return message, ecc_message, message_raw


def compress_image(image, quality):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    result, encimg = cv2.imencode(".jpg", image, encode_param)
    if not result:
        raise Exception("Could not compress image")
    image = cv2.imdecode(encimg, 1)
    return image


def calculate_accuracy(payload1: bytes, payload2: bytes):
    repeats, remainder = divmod(len(payload2), len(payload1))
    if remainder > 0:
        print("Payloads have different lengths")

    payload1 = payload1 * repeats + payload1[:remainder]

    arr_original = np.frombuffer(payload1, dtype=np.uint8)
    arr_retrieved = np.frombuffer(payload2, dtype=np.uint8)

    # Convert bytes to bits
    arr_original_bits = np.unpackbits(arr_original)
    arr_retrieved_bits = np.unpackbits(arr_retrieved)

    # Compare bits
    matching_bits = np.sum(arr_original_bits == arr_retrieved_bits)
    total_bits = arr_original_bits.size

    return matching_bits / total_bits
