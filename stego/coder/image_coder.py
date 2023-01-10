import logging
from itertools import cycle

import numpy as np

from stego.coder.message import message_to_dec, dec_to_message, Base2MessageCoder
from stego.coder.transform.blocking import CropBlocker
from collections import Counter
import unireedsolomon as rs
import cv2


class StegoCoder:
    def __init__(self, transform, message_length):
        self.transform = transform
        self.message_length = message_length
        self.message_coder = rs.RSCoder(128, message_length)

    def _loop_message(self, message):
        return cycle(message)

    def find_original_string(self, strings):
        # Initialize the result string with the same length as the input strings
        result = ['-'] * len(strings[0])

        # Iterate through each position in the strings
        for i in range(len(strings[0])):
            # Count the number of occurrences of each character at this position
            count = Counter([string[i] for string in strings])
            # Find the character with the highest count
            most_common = count.most_common(1)[0][0]
            # Add the most common character to the result string
            result[i] = most_common

        # Join the result list into a single string
        result_string = ''.join(result)

        return result_string

    def prepare_message(self, message):
        msg = self.message_coder.encode(message)
        msg = message_to_dec(msg)
        return self._loop_message(msg)

    def decode_message(self, retrieved_data):
        message_raw = dec_to_message(retrieved_data)
        data = self.split_list(message_raw, 128)
        messages = []
        for s in data[:20]:
            print(s)
            try:
                message, _ = self.message_coder.decode(s)
            except:
                continue
            messages.append(message)

        result = self.find_original_string(messages)

        return result

    def split_list(self, arr, sublist_size):
        # pad a list
        if len(arr) % sublist_size != 0:
            arr += "" * (sublist_size - (len(arr) % sublist_size))
        return [arr[x:x + sublist_size] for x in range(0, len(arr), sublist_size)]

    def encode(self, img, message):
        self.transform.forward(img)
        ll = self.transform.coefficients[0]
        coefficients = self.transform.coefficients[-1]

        msg_iterator = iter(self.prepare_message(message))
        coefficients_new = [codec.encode_band(
            band, msg_iterator) for band in coefficients]

        self.transform.coefficients[-1] = tuple(coefficients_new)

        return self.transform.inverse()

    def decode(self, img):
        self.transform.forward(img)
        ll = self.transform.coefficients[0]
        coefficients = self.transform.coefficients[-1]

        extracted_data = []

        for band in coefficients:
            extracted_data += codec.decode_band(band)

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
        self.message_coder = rs.RSCoder(128, MSG_LEN)
        self.levels_to_encode = levels_to_encode
        self.alpha = alpha
        self.quality_level = quality_level

    def get_mvs(self, image, quality_level=50):
        comp = compress_image(image, quality_level)
        mvs = get_diffs(image, comp, self.transform)
        return mvs

    def _loop_message(self, message):
        return cycle(message)

    def find_original_string(self, strings):
        # Initialize the result string with the same length as the input strings
        result = [' '] * MSG_LEN

        # Iterate through each position in the strings
        for i in range(len(strings[0])):
            # Count the number of occurrences of each character at this position
            count = Counter([string[i] for string in strings])
            # Find the character with the highest count
            most_common = count.most_common(1)[0][0]
            # Add the most common character to the result string
            result[i] = most_common

        # Join the result list into a single string
        result_string = ''.join(result)

        return result_string[:MSG_LEN]

    def encode_message(self, message: str):
        message = message.ljust(MSG_LEN)
        message = self.message_coder.encode(message=message)
        msg = Base2MessageCoder.encode(message)
        return self._loop_message(msg)

    def decode_message(self, retrieved_data):
        message_raw = Base2MessageCoder.decode(retrieved_data)
        data = self.split_list(message_raw, 128)
        messages = []
        for s in data[:-1]:
            try:
                s = self.message_coder.decode(s)
            except:
                continue
            messages.append(s)
        logging.info(f"{len(data)=},{len(messages)=},{len(messages)/len(data)}")
        result = self.find_original_string(messages)

        return result

    def split_list(self, arr, sublist_size):
        # pad a list
        if len(arr) % sublist_size != 0:
            arr += "" * (sublist_size - (len(arr) % sublist_size))
        return [arr[x:x + sublist_size] for x in range(0, len(arr), sublist_size)]

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

        msg_iterator = iter(self.encode_message(message))

        new_coefficients = []
        for level, mvs in zip(levels[1:self.levels_to_encode + 1], all_mvs[1:self.levels_to_encode + 1]):
            new_coefficients.append(
                tuple(
                    self.encode_band(band, msg_iterator, mv) for band, mv in zip(level, mvs)
                )
            )

        self.transform.coefficients[1:self.levels_to_encode +
                                      1] = new_coefficients

        return self.transform.inverse()

    def decode(self, img):
        self.transform.forward(img)

        extracted_data = []

        for level in self.transform.coefficients[1:self.levels_to_encode + 1]:
            for band in level:
                extracted_data += self.decode_band(band)

        return self.decode_message(extracted_data)

    def encode_color_image(self, img, message):
        color_bands = []
        for color in cv2.split(img):
            color_bands.append(self.encode(color, message))

        return cv2.merge(color_bands)

    def decode_color_image(self, img):
        extracted_data = []

        for color in cv2.split(img):
            self.transform.forward(color)
            for level in self.transform.coefficients[1:self.levels_to_encode + 1]:
                for band in level:
                    extracted_data += self.decode_band(band)

            return self.decode_message(extracted_data)
