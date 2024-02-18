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

color_spaces_inversed = {
    "RGB": None,
    "YCrCb": cv2.COLOR_YCrCb2RGB,
    "HSV": cv2.COLOR_HSV2RGB,
    "HLS": cv2.COLOR_HLS2RGB,
    "Lab": cv2.COLOR_Lab2RGB,
    "Luv": cv2.COLOR_Luv2RGB,
    "YUV": cv2.COLOR_YUV2RGB,
    "XYZ": cv2.COLOR_XYZ2RGB,
}


def rgb_to_color_space(image: np.ndarray, color_space: str) -> np.ndarray:
    """Converts an image to a different color space."""
    if color_space == "RGB":
        return image
    else:
        return cv2.cvtColor(image, color_spaces.get(color_space, cv2.COLOR_RGB2YCrCb))


def color_space_to_rgb(image: np.ndarray, color_space: str) -> np.ndarray:
    """Converts an image from a different color space to RGB."""
    if color_space == "RGB":
        return image
    else:
        return cv2.cvtColor(
            image, color_spaces_inversed.get(color_space, cv2.COLOR_YCrCb2RGB)
        )


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
) -> (np.ndarray, np.ndarray, bytes):
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

    image, _ = blocking.crop_image_to_divisible(image, block_size * 2**level)

    message_parts = coder.message_dispatcher(image, ecc_message, **parameters)
    channels = list(cv2.split(rgb_to_color_space(image, color_space)))

    for channel_index in use_channels:
        channel = channels[channel_index]
        encoded_channel = coder.encode(channel, message_parts, **parameters)
        channels[channel_index] = encoded_channel

    stego = color_space_to_rgb(cv2.merge(channels), color_space)
    return image, stego, b"".join(message_parts)


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
) -> (bytearray | None, bytes, bytes):
    """Decodes a message from a color image."""
    parameters = {
        "coefficients": coefficients,
        "block_size": block_size,
        "level": level,
        "wavelet": wavelet,
        "ecc_symbols": ecc_symbols,
    }

    channels = cv2.split(rgb_to_color_space(image, color_space))

    message_parts = []
    for channel_index in use_channels:
        message_parts += coder.decode(channels[channel_index], **parameters)

    message_raw = coder.message_consolidator(image, message_parts, **parameters)
    ecc_message = msg_utils.find_original_string(message_raw)
    try:
        message, message_ecc, _ = msg_utils.decode_ecc(ecc_message, **parameters)
        if not message:
            message = message_ecc
    except ReedSolomonError:
        message = None
    return message, ecc_message, message_raw
