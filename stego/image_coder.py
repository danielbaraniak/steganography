from itertools import cycle

import numpy as np

from stego import codec
from stego.message import message_to_dec, dec_to_message, Base2MessageCoder
from stego.transform.blocking import CropBlocker
from stego.transform.dwt import Iwt
from collections import Counter
import unireedsolomon as rs


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


class RobustStegoCoder:
    def __init__(self, transform, codec):
        self.transform = transform
        self.codec = codec

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
        msg = Base2MessageCoder.encode(message)
        return self._loop_message(msg)

    def decode_message(self, retrieved_data):
        message_raw = Base2MessageCoder.decode(retrieved_data)
        data = self.split_list(message_raw, 128)
        messages = []
        for s in data[:5]:
            print(s)
            messages.append(s)

        result = self.find_original_string(messages)

        return result

    def split_list(self, arr, sublist_size):
        # pad a list
        if len(arr) % sublist_size != 0:
            arr += "" * (sublist_size - (len(arr) % sublist_size))
        return [arr[x:x + sublist_size] for x in range(0, len(arr), sublist_size)]

    def encode_band(self, band: np.ndarray, message_iterator):
        blocker = CropBlocker(band)
        blocks = blocker.divide(block_size=3)
        for j, row in enumerate(blocks):
            try:
                for k, block in enumerate(row):
                    blocks[j][k] = embed(block, next(message_iterator))
            except StopIteration:
                break
        return blocker.stack(blocks)

    def decode_band(self, band):
        blocker = CropBlocker(band)
        blocks = blocker.divide(block_size=3)
        encoded_data = []

        for row in blocks:
            for block in row:
                pass
        return encoded_data

    def encode(self, img, message):
        coeffs = self.transform.forward(img)
        coefficients = self.transform.coefficients[-1]

        msg_iterator = iter(self.prepare_message(message))
        coefficients_new = [self.encode_band(
            band, msg_iterator) for band in coefficients]

        self.transform.coefficients[-1] = tuple(coefficients_new)

        return self.transform.inverse()

    def decode(self, img):
        self.transform.forward(img)
        ll = self.transform.coefficients[0]
        coefficients = self.transform.coefficients[-1]

        extracted_data = []

        for band in coefficients:
            extracted_data += self.decode_band(band)

        return self.decode_message(extracted_data)
