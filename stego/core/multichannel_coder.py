import cv2
import numpy as np
from reedsolo import ReedSolomonError

from stego.core import blocking
from stego.core import coder
from stego.core import message as msg_utils

color_spaces = {
    "RGB": None,
    "YCrCb": cv2.COLOR_RGB2YCrCb,
    "HSV": cv2.COLOR_RGB2HSV,
    "HLS": cv2.COLOR_RGB2HLS,
    "Lab": cv2.COLOR_RGB2Lab,
    "Luv": cv2.COLOR_RGB2Luv,
    "YUV": cv2.COLOR_RGB2YUV,
    "XYZ": cv2.COLOR_RGB2XYZ,
}


def encode_color_image(
        image: np.ndarray,
        message: bytes,
        *,
        coefficients: list[str],
        alpha: float = 1,
        block_size: int = 3,
        level: int = 2,
        wavelet: str = "haar",
        color_space: str,
        use_channels: list[int],
        ecc_symbols: int,
        **kwargs,
) -> (np.ndarray, np.ndarray, list[bytearray]):
    """Encodes a message into a color image."""
    parameters = {
        "coefficients": coefficients,
        "alpha": alpha,
        "block_size": block_size,
        "level": level,
        "wavelet": wavelet,
        "ecc_symbols": ecc_symbols,
    }

    ecc_message = msg_utils.encode_ecc(message, **parameters)

    image, _ = blocking.crop_image_to_divisible(image, block_size * 2 ** level)

    message_parts = coder.uniform_message_dispatcher(image, ecc_message, **parameters)
    channels = list(
        cv2.split(
            cv2.cvtColor(image, color_spaces.get(color_space, cv2.COLOR_RGB2YCrCb))
        )
    )

    for channel_index in use_channels:
        channel = channels[channel_index]
        encoded_channel = coder.encode(channel, message_parts, **parameters)
        channels[channel_index] = encoded_channel

    stego = cv2.cvtColor(cv2.merge(channels), cv2.COLOR_YCrCb2RGB)
    return image, stego, message_parts


def decode_color_image(
        image: np.ndarray,
        *,
        coefficients: list[str],
        block_size: int = 3,
        level: int = 2,
        wavelet: str = "haar",
        color_space: str,
        use_channels: list[int],
        ecc_symbols: int,
        **kwargs,
) -> (bytearray, list[bytes]):
    """Decodes a message from a color image."""
    parameters = {
        "coefficients": coefficients,
        "block_size": block_size,
        "level": level,
        "wavelet": wavelet,
        "ecc_symbols": ecc_symbols,
    }

    channels = cv2.split(
        cv2.cvtColor(image, color_spaces.get(color_space, cv2.COLOR_RGB2YCrCb))
    )

    message_parts = []
    for channel_index in use_channels:
        message_parts += coder.decode(channels[channel_index], **parameters)

    message = coder.message_consolidator(image, message_parts, **parameters)
    ecc_message = msg_utils.find_original_string(message)
    try:
        message, message_ecc, _ = msg_utils.decode_ecc(ecc_message, **parameters)
        if not message:
            message = message_ecc
    except ReedSolomonError:
        message = None
    return message, message_parts
