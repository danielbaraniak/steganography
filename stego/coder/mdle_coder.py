import numpy as np
from reedsolo import ReedSolomonError, RSCodec

from stego.coder.message import (
    loop_message,
    find_original_string,
    Base4MessageCoder,
    split_list,
)

from stego.coder.transform.blocking import CropBlocker

coeffs_order = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0)]


def is_edge_block(block, T=4):
    U = []
    center = block[1, 1]
    for idx in coeffs_order:
        di = abs(center - block[idx])
        U.append(di)
    V = max(U) / 4
    C = 0
    for g in U:
        if g >= V:
            C += 1
    return C > T


def extraction_function(pi, pc):
    return (pi + pc) % 4


def lcv(S, f):
    return (S - f) % 4


lcv_to_mv = [0, 1, 2, -1]


def embed(block, decimal_data: np.ndarray):
    center_coeff = block[1, 1]
    perimeter_coeffs = np.array([block[idx] for idx in coeffs_order])
    lcvs = lcv(decimal_data, extraction_function(perimeter_coeffs, center_coeff))
    mvs = [lcv_to_mv[int(lcv)] for lcv in lcvs]

    for idx, mv in zip(coeffs_order, mvs):
        block[idx] += mv

    return block


def extract(block):
    center_coeff = block[1, 1]
    perimeter_coeffs = np.array([block[idx] for idx in coeffs_order])
    return extraction_function(perimeter_coeffs, center_coeff)


def encode_band(band: np.ndarray, message_iterator):
    blocker = CropBlocker(band)
    blocks = blocker.divide(block_size=3)
    for j, row in enumerate(blocks):
        try:
            for k, block in enumerate(row):
                blocks[j][k] = embed(block, next(message_iterator))
        except StopIteration:
            break
    return blocker.stack(blocks)


def decode_band(band):
    blocker = CropBlocker(band)
    blocks = blocker.divide(block_size=3)
    encoded_data = []

    for row in blocks:
        for block in row:
            encoded_data.extend(extract(block))
    return encoded_data


class MdleCoder:
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
        coefficients_new = [encode_band(band, msg_iterator) for band in coefficients]

        self.transform.coefficients[-1] = tuple(coefficients_new)

        return self.transform.inverse()

    def decode(self, img):
        self.transform.forward(img)
        coefficients = self.transform.coefficients[-1]

        extracted_data = []

        for band in coefficients:
            extracted_data += decode_band(band)

        return self.decode_message(extracted_data)
