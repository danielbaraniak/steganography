import numpy as np
import pywt

import stego.core.message as msg_utils
import stego.core.blocking as blocking
from stego.core.errors import CapacityError
import logging

BYTE = 8


def modify_blocks(
    message: bytes, blocks: list[np.ndarray], bit_step: int, alpha: float
) -> np.ndarray:
    message_bin: np.ndarray = msg_utils.bytes_to_binary(message).astype(int)
    blocks = np.array(blocks)
    center_index = blocks.shape[1] // 2, blocks.shape[2] // 2
    mv = message_bin * bit_step * 2 - bit_step
    mean_values = np.nanmean(blocks, axis=(1, 2))[: message_bin.size]
    blocks[: message_bin.size, *center_index] = mean_values + alpha * mv

    return blocks


def decode_blocks(blocks: list[np.ndarray]) -> bytes:
    blocks = np.array(blocks)
    center_index = blocks.shape[1] // 2, blocks.shape[2] // 2

    center_values = blocks[:, *center_index].copy()
    blocks[:, *center_index] = np.nan
    mean_values = np.nanmean(blocks, axis=(1, 2))

    differences = center_values - mean_values
    inferred_bits = differences > 0

    message = msg_utils.binary_to_bytes(inferred_bits)
    return message


def encode(
    image: np.ndarray,
    message_parts: list[bytes],
    *,
    coefficients: list[str],
    alpha: float = 1,
    block_size: int = 3,
    level: int = 2,
    wavelet: str = "haar",
    **kwargs,
) -> np.ndarray:
    bit_step = 2**level
    decomposition = pywt.wavedecn(image, wavelet=wavelet, level=level)
    for coefficient, message in zip(coefficients, message_parts):
        cover = decomposition[1][coefficient]
        blocks = blocking.divide_image(cover, block_size=block_size)
        modified_blocks = modify_blocks(message, blocks, bit_step, alpha)
        decomposition[1][coefficient] = blocking.merge_blocks(
            modified_blocks, cover.shape
        )

    stego = pywt.waverecn(decomposition, wavelet=wavelet)
    stego = np.clip(stego, 0, 255).astype(np.uint8)
    return stego


def decode(
    image: np.ndarray,
    *,
    coefficients: list[str],
    block_size: int = 3,
    level: int = 2,
    wavelet: str = "haar",
    **kwargs,
) -> list[bytes]:
    decomposition = pywt.wavedecn(image, wavelet=wavelet, level=level)
    message_parts = []
    for coefficient in coefficients:
        cover = decomposition[1][coefficient]
        blocks = blocking.divide_image(cover, block_size=block_size)
        message = decode_blocks(blocks)
        message_parts.append(message)
    logging.debug(f"Message parts: {message_parts}")
    return message_parts


def get_capacity(
    image: np.ndarray,
    *,
    coefficients: list[str],
    block_size: int = 3,
    level: int = 2,
    **kwargs,
) -> tuple[int, int]:
    """Calculates the capacity of the image in bytes."""
    initial_block_size = block_size * 2**level
    height, width = image.shape[:2]
    coefficient_capacity = (
        height // initial_block_size * width // initial_block_size
    ) // BYTE
    image_capacity = coefficient_capacity * len(coefficients)
    return image_capacity, coefficient_capacity


def message_dispatcher(
    image: np.ndarray,
    message: bytes,
    *,
    coefficients: list[str],
    block_size: int = 3,
    level: int = 2,
    **kwargs,
):
    """Divides the message into parts that fit into coefficients of the image."""
    image_capacity, coefficient_capacity = get_capacity(
        image, block_size=block_size, level=level, coefficients=coefficients
    )

    message = message + b"\x00"

    if image_capacity < len(message):
        raise CapacityError(
            f"Message is too long for the image. Image capacity: {image_capacity}, message length: {len(message)}"
        )

    fits, remainder = divmod(image_capacity, len(message))
    new_message = message * fits + b"\x00" * remainder
    message_parts = [
        new_message[i : i + coefficient_capacity]
        for i in range(0, len(new_message), coefficient_capacity)
    ]
    logging.debug(f"Message parts: {message_parts}")
    return message_parts


def uniform_message_dispatcher(
    image: np.ndarray,
    message: bytes,
    *,
    coefficients: list[str],
    block_size: int = 3,
    level: int = 2,
    **kwargs,
):
    """Create identical parts that fit into coefficients of the image."""
    image_capacity, coefficient_capacity = get_capacity(
        image, block_size=block_size, level=level, coefficients=coefficients
    )

    message = message + b"\x00"

    if coefficient_capacity < len(message):
        raise CapacityError(
            f"Message is too long for the coefficient. Coefficient capacity: "
            f"{coefficient_capacity}, message length: {len(message)}"
        )
    fits, remainder = divmod(coefficient_capacity, len(message))
    padded_message = message * fits + b"\x00" * remainder

    message_parts = [padded_message] * len(coefficients)
    return message_parts


def message_consolidator(
    image: np.ndarray,
    message_parts: list[bytes],
    *,
    coefficients: list[str],
    block_size: int = 3,
    level: int = 2,
    **kwargs,
) -> bytes:
    """Consolidates the messages extracted from coefficients."""
    image_capacity, coefficient_capacity = get_capacity(
        image, block_size=block_size, level=level, coefficients=coefficients
    )
    trimmed_message_parts = [
        message_part[:coefficient_capacity] for message_part in message_parts
    ]
    return b"".join(trimmed_message_parts)
