import numpy as np

from stego.transform import blocking
from stego.transform.blocking import CropBlocker

coeffs_order = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0)]


def is_edge_block(block, T=4):
    U = []
    center = block[1, 1]
    for idx in coeffs_order:
        di = abs(center - block[idx])
        U.append(di)
        # print(f'{block[idx]=}')
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
