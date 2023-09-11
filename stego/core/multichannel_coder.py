import cv2
import numpy as np

from stego.core.coder import message_dispatcher, encode, message_consolidator, decode
from stego.core import message as msg_utils


def encode_color_image(
    image: np.ndarray,
    message: bytes,
    *,
    coefficients: list[str],
    alpha: float = 1,
    block_size: int = 3,
    level: int = 2,
    wavelet: str = "haar"
) -> np.ndarray:
    """Encodes a message into a color image."""
    parameters = {
        "coefficients": coefficients,
        "alpha": alpha,
        "block_size": block_size,
        "level": level,
        "wavelet": wavelet,
    }

    message_parts = message_dispatcher(image, message, **parameters)
    channels = cv2.split(cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb))
    stego_channels = [
        encode(channel, message_parts, **parameters) for channel in channels
    ]
    stego = cv2.cvtColor(cv2.merge(stego_channels), cv2.COLOR_YCrCb2RGB)
    return stego


def decode_color_image(
    image: np.ndarray,
    *,
    coefficients: list[str],
    block_size: int = 3,
    level: int = 2,
    wavelet: str = "haar",
    **kwargs
) -> bytes:
    """Decodes a message from a color image."""
    parameters = {
        "coefficients": coefficients,
        "block_size": block_size,
        "level": level,
        "wavelet": wavelet,
    }

    channels = cv2.split(cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb))

    message_parts = []
    for channel in channels:
        message_parts += decode(channel, **parameters)
    message = message_consolidator(image, message_parts, **parameters)
    return msg_utils.extract_repeating_fragment(message)
