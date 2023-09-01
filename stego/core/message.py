import numpy as np


def bytes_to_binary(byte_data: bytes) -> np.ndarray:
    byte_array = np.frombuffer(byte_data, dtype=np.uint8)
    binary_representation = np.unpackbits(byte_array)
    return binary_representation


def binary_to_bytes(binary_data: np.ndarray) -> bytes:
    byte_array = np.packbits(binary_data)
    return byte_array.tobytes()
