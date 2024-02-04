import numpy as np
from reedsolo import ReedSolomonError, RSCodec

rsc = RSCodec(10)


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


def encode_ecc(message: bytes):
    return rsc.encode(message)


def decode_ecc(message: bytes):
    return rsc.decode(message)
