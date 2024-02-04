import numpy as np
from scipy import stats
from reedsolo import ReedSolomonError, RSCodec





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


def find_original_string(message: bytes):
    fragments = message.split(b'\x00')
    max_len = max([len(fragment) for fragment in fragments])

    messages = [np.frombuffer(fragment.ljust(max_len, b'\x00'), dtype=np.uint8)
                for fragment in fragments
                if len(fragment) > 5]

    messages = np.array(messages)

    modes, _ = stats.mode(messages)

    result_message = modes.astype(np.uint8).tobytes()
    result_message = result_message.rstrip(b'\x00')
    return result_message


def encode_ecc(message: bytes, ecc_symbols, **kwargs):
    rsc = RSCodec(ecc_symbols)
    return rsc.encode(message)


def decode_ecc(message: bytes, ecc_symbols, **kwargs):
    rsc = RSCodec(ecc_symbols)
    return rsc.decode(message)
