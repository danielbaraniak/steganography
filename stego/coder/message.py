from collections import Counter
from itertools import cycle

import numpy as np
from reedsolo import ReedSolomonError, RSCodec


class MessageNotFoundException(Exception):
    pass


def loop_message(message):
    return cycle(message)


def split_list(arr, sublist_size):
    arr = np.array(arr)
    if arr.size % sublist_size:
        pad_width = sublist_size - (arr.size % sublist_size)
        arr = np.pad(arr, (0, pad_width), "constant", constant_values=(0, 0))
    return np.reshape(arr, (arr.size // sublist_size, sublist_size))


def find_original_string(strings):
    if not strings:
        raise MessageNotFoundException

    # Initialize the result string with the same length as the input strings

    msg_len = min([len(s) for s in strings])
    result = bytearray([0] * msg_len)

    # Iterate through each position in the strings
    for i in range(msg_len):
        # Count the number of occurrences of each character at this position
        count = Counter([string[i] for string in strings])
        # Find the character with the highest count
        most_common = count.most_common(1)[0][0]
        # Add the most common character to the result string
        result[i] = most_common

    return result


class MessageCoder:
    @staticmethod
    def encode(msg):
        ...

    @staticmethod
    def decode(encoded_data):
        ...


class Base4MessageCoder(MessageCoder):
    @staticmethod
    def _byte_to_dec_array(byte):
        result = [None, None, None, None]
        result[0] = (byte & 0b11000000) >> 6
        result[1] = (byte & 0b00110000) >> 4
        result[2] = (byte & 0b00001100) >> 2
        result[3] = byte & 0b00000011

        return result

    @staticmethod
    def _dec_array_to_byte(encoded_data):
        result = 0
        result |= int(encoded_data[0]) << 6
        result |= int(encoded_data[1]) << 4
        result |= int(encoded_data[2]) << 2
        result |= int(encoded_data[3])

        return result

    @staticmethod
    def encode(msg: str):
        byte_message = bytes(msg, "utf-8")
        arr = []
        for b in byte_message:
            arr.extend(Base4MessageCoder._byte_to_dec_array(b))

        return split_list(arr, 8)

    @staticmethod
    def decode(arr):
        arr = [int(i) for i in arr]
        chunks = split_list(arr, 4)

        dec_list = []
        for chunk in chunks:
            dec_list.append(Base4MessageCoder._dec_array_to_byte(chunk))

        return bytes(dec_list).decode("utf-8", errors="ignore")


def encode_message(message: str, capacity: int):
    rsc = RSCodec(capacity - len(message))
    encoded_message = rsc.encode(message.encode("ascii"))
    arr = np.array(encoded_message)
    return np.unpackbits(arr)


def decode_message(retrieved_data: list, capacity: int):
    byte_values = np.packbits(retrieved_data)
    raw_message = bytearray(byte_values.flatten())
    if len(raw_message) >= 128:
        raw_message = raw_message[:128]

    result = None

    for i in range(min(capacity, 128)):
        try:
            rsc = RSCodec(i)
            decoded = rsc.decode(raw_message)
            if decoded[0] and decoded[0][0]:
                decoded[0].decode("ascii")
                result = decoded
        except ReedSolomonError:
            continue
        except UnicodeDecodeError:
            continue

    if result is None:
        raise MessageNotFoundException

    return result
