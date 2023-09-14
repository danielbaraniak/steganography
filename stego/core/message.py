import numpy as np


def bytes_to_binary(byte_data: bytes) -> np.ndarray:
    byte_array = np.frombuffer(byte_data, dtype=np.uint8)
    binary_representation = np.unpackbits(byte_array)
    return binary_representation


def binary_to_bytes(binary_data: np.ndarray | list[int]) -> bytes:
    byte_array = np.packbits(binary_data)
    return byte_array.tobytes()


def extract_repeating_fragment(message: bytes):
    fragments = message.split(b'\x00')
    fragment_occurrences = {fragment: fragments.count(fragment) for fragment in fragments if len(fragment) > 5}
    most_frequent_fragment = max(fragment_occurrences, key=fragment_occurrences.get)
    return most_frequent_fragment
