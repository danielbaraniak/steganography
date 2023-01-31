import logging

import cv2
import numpy as np
from reedsolo import ReedSolomonError, RSCodec

from stego.coder import mdle_codec
from stego.coder.message import loop_message, find_original_string, encode_message, decode_message, Base4MessageCoder, \
    split_list
from stego.coder.transform.blocking import CropBlocker


class StegoCoder:
    def __init__(self, transform, message_length):
        self.transform = transform
        self.message_length = message_length
        self.message_coder = RSCodec(128 - message_length)

    def prepare_message(self, message):
        msg = self.message_coder.encode(message)
        msg = Base4MessageCoder.encode(msg)
        return loop_message(msg)

    def decode_message(self, retrieved_data):
        message_raw = Base4MessageCoder.decode(retrieved_data)
        data = split_list(message_raw, 128)
        messages = []
        for s in data[:20]:
            print(s)
            try:
                message, _ = self.message_coder.decode(s)
            except ReedSolomonError:
                continue
            messages.append(message)

        result = find_original_string(messages)

        return result

    def encode(self, img, message):
        self.transform.forward(img)
        coefficients = self.transform.coefficients[-1]

        msg_iterator = iter(self.prepare_message(message))
        coefficients_new = [mdle_codec.encode_band(
            band, msg_iterator) for band in coefficients]

        self.transform.coefficients[-1] = tuple(coefficients_new)

        return self.transform.inverse()

    def decode(self, img):
        self.transform.forward(img)
        coefficients = self.transform.coefficients[-1]

        extracted_data = []

        for band in coefficients:
            extracted_data += mdle_codec.decode_band(band)

        return self.decode_message(extracted_data)


perimeter_mask = np.array([
    [True, True, True],
    [True, False, True],
    [True, True, True]
])

MSG_LEN = 30


def compress_image(image, quality_level):
    _, compressed_image_bytes = cv2.imencode(
        ".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality_level])
    compressed_image_array = cv2.imdecode(np.frombuffer(
        compressed_image_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)

    return compressed_image_array


def sigma(data, n):
    mean = np.mean(data)
    std = np.std(data)
    return max(abs(mean - n * std), abs(mean + n * std))


def get_diffs(original, modified, transform):
    o_coeffs = transform.forward(original)
    m_coeffs = transform.forward(modified)

    diffs = []
    diff = o_coeffs[0] - m_coeffs[0]
    diffs.append(sigma(diff, 2))

    for o, m in zip(o_coeffs[1:], m_coeffs[1:]):
        level = []
        for i in range(3):
            diff = o[i] - m[i]
            level.append(sigma(diff, 2))
        diffs.append(level)
    return diffs


class RobustStegoCoder:
    def __init__(self, transform, levels_to_encode: int = 1, quality_level=50, alpha: float = 1):
        self.transform = transform
        self.levels_to_encode = levels_to_encode
        self.alpha = alpha
        self.quality_level = quality_level

    def get_mvs(self, image, quality_level=50):
        comp = compress_image(image, quality_level)
        mvs = get_diffs(image, comp, self.transform)
        return mvs

    def encode_block(self, block, data, mv, alpha):

        mean = np.mean(block, where=perimeter_mask)
        new_value = mean
        if data == 0:
            new_value -= mv * alpha
        elif data == 1:
            new_value += mv * alpha
        block[1, 1] = new_value

        return block

    def decode_block(self, block):
        m = np.mean(block, where=perimeter_mask)
        value = block[1, 1] - m
        result = 0
        if value > 0:
            result = 1
        elif value < 0:
            result = 0
        return result

    def encode_band(self, band: np.ndarray, message_iterator, mv):
        blocker = CropBlocker(band)
        blocks = blocker.divide(block_size=3)
        for j, row in enumerate(blocks):
            try:
                for k, block in enumerate(row):
                    blocks[j][k] = self.encode_block(
                        block, next(message_iterator), mv, alpha=self.alpha)
            except StopIteration:
                break
        return blocker.stack(blocks)

    def decode_band(self, band):
        blocker = CropBlocker(band)
        blocks = blocker.divide(block_size=3)
        encoded_data = []

        for row in blocks:
            for block in row:
                encoded_data.append(self.decode_block(block))

        return encoded_data

    def encode(self, img, message):
        all_mvs = self.get_mvs(img, self.quality_level)
        levels = self.transform.forward(img)[:]

        msg_iterator = iter(encode_message(message, 128))

        new_coefficients = []
        for level, mvs in zip(levels[1:self.levels_to_encode + 1], all_mvs[1:self.levels_to_encode + 1]):
            new_coefficients.append(
                tuple(
                    self.encode_band(band, msg_iterator, mv) for band, mv in zip(level, mvs)
                )
            )

        self.transform.coefficients[1:self.levels_to_encode + 1] = new_coefficients

        return self.transform.inverse()

    def decode(self, img):
        self.transform.forward(img)

        extracted_data = []

        for level in self.transform.coefficients[1:self.levels_to_encode + 1]:
            for band in level:
                extracted_data += self.decode_band(band)

        return decode_message(extracted_data, 128)[0]

    def encode_color_image(self, img, message):
        color_bands = []
        for color in cv2.split(img):
            color_bands.append(self.encode(color, message))

        return cv2.merge(color_bands)

    def decode_color_image(self, img):

        metadata = self.decode_color_image_verbose(img)

        logging.info(f"R{metadata[0]},B{metadata[1]},G{metadata[2]}")

        msgs = []
        for m, _, _ in metadata:
            msgs.append(m)

        return find_original_string(msgs).decode('ascii')

    def decode_color_image_verbose(self, img):
        channel_messages = []

        for color in cv2.split(img):
            extracted_data = []
            self.transform.forward(color)
            for level in self.transform.coefficients[1:self.levels_to_encode + 1]:
                for band in level:
                    extracted_data += self.decode_band(band)

            channel_messages.append(decode_message(extracted_data, 128))

        return channel_messages

    def __str__(self) -> str:
        return f"{str(self.transform.wavelet)}_{str(self.transform.level)}_q({self.quality_level})"
