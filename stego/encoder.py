import numpy as np
from stego.transform.blocking import divide_image, stack_image
from stego.transform.dct import dct, idct


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


def prepare_message(msg):
    import unireedsolomon as rs
    coder = rs.RSCoder(20, 13)
    c = coder.encode("Hello, world!")
    coder.decode()
