import numpy as np
from stego.transform.blocking import divide_image, stack_image
from stego.transform.dct import dct, idct

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
    perimiter_coeffs = np.array([block[idx] for idx in coeffs_order])
    lcvs = lcv(decimal_data, extraction_function(perimiter_coeffs, center_coeff))
    mvs = [lcv_to_mv[int(lcv)] for lcv in lcvs]

    for idx, mv in zip(coeffs_order, mvs):
        block[idx] += mv

    return block


def extract(block):
    center_coeff = block[1, 1]
    perimiter_coeffs = np.array([block[idx] for idx in coeffs_order])
    return extraction_function(perimiter_coeffs, center_coeff)


def encode_block(block, payload, alpha):
    print(block)
    block[0, 0], dc = float('-inf'), block[0, 0]

    max_position = np.unravel_index(np.argmax(block), block.shape)
    block[max_position] += int(payload) * alpha
    block[0, 0] = dc
    return block


def decode_block(c_block, s_block, alpha):
    s_block[0, 0] = float('-inf')

    max_position = np.unravel_index(np.argmax(s_block), s_block.shape)

    payload = s_block[max_position] - c_block[max_position]

    return int(payload / alpha)


def encode(cover_img: np.ndarray, payload, block_size: int = 8, alpha: float = 1):
    blocks = divide_image(cover_img, block_size=block_size)

    payload_iterator = iter(payload)

    for i, column in enumerate(blocks):
        for j, block in enumerate(column):
            try:
                w = next(payload_iterator)
            except StopIteration:
                break
            dct_block = dct(block)
            encode_block(dct_block, w, alpha=alpha)
            blocks[i][j] = idct(dct_block)

    return stack_image(blocks)


def decode(stego_img, cover_img, block_size: int = 8, alpha: float = 1):
    c_blocks = divide_image(cover_img, block_size=block_size)
    s_blocks = divide_image(stego_img, block_size=block_size)

    payload = []

    for i, column in enumerate(zip(c_blocks, s_blocks)):
        for j, block in enumerate(column):
            c_dct = dct(block[0])
            s_dct = dct(block[1])

            payload.append(decode_block(c_dct, s_dct, alpha))

    return payload


def byte_to_dec_array(byte):
    result = [None, None, None, None]
    result[0] = (byte & 0b11000000) >> 6
    result[1] = (byte & 0b00110000) >> 4
    result[2] = (byte & 0b00001100) >> 2
    result[3] = (byte & 0b00000011)

    return result


def dec_array_to_byte(encoded_data):
    result = 0
    result |= int(encoded_data[0]) << 6
    result |= int(encoded_data[1]) << 4
    result |= int(encoded_data[2]) << 2
    result |= int(encoded_data[3])

    return result


def message_to_dec(msg: str):
    byte_message = bytes(msg, 'utf-8')
    arr = []
    for b in byte_message:
        arr.extend(byte_to_dec_array(b))

    return split_list(arr, 8)


def dec_to_message(arr):
    arr = [int(i) for i in arr]
    chunks = split_list(arr, 4)

    dec_list = []
    for chunk in chunks:
        dec_list.append(dec_array_to_byte(chunk))

    return bytes(dec_list).decode('utf-8', errors='ignore')


def split_list(arr, sublist_size):
    # pad a list
    arr += [0] * (sublist_size - (len(arr) % sublist_size))
    return [arr[x:x + sublist_size] for x in range(0, len(arr), sublist_size)]


def encode_band(band: list, message_iterator):
    for j, row in enumerate(band):
        try:
            for k, block in enumerate(row):
                band[j][k] = embed(block, next(message_iterator))
        except StopIteration:
            break


def decode_band(blocks):
    encoded_data = []
    for row in blocks:
        for block in row:
            encoded_data.extend(extract(block))
    return encoded_data
