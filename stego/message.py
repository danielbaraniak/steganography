def byte_to_dec_array(byte):
    result = [None, None, None, None]
    result[0] = (byte & 0b11000000) >> 6
    result[1] = (byte & 0b00110000) >> 4
    result[2] = (byte & 0b00001100) >> 2
    result[3] = (byte & 0b00000011)

    return result


def dec_array_to_byte(encoded_data):
    result = 0
    result |= int(encoded_data[0]) << 6
    result |= int(encoded_data[1]) << 4
    result |= int(encoded_data[2]) << 2
    result |= int(encoded_data[3])

    return result


def message_to_dec(msg: str):
    byte_message = bytes(msg, 'utf-8')
    arr = []
    for b in byte_message:
        arr.extend(byte_to_dec_array(b))

    return _split_list(arr, 8)


def dec_to_message(arr):
    arr = [int(i) for i in arr]
    chunks = _split_list(arr, 4)

    dec_list = []
    for chunk in chunks:
        dec_list.append(dec_array_to_byte(chunk))

    return bytes(dec_list).decode('utf-8', errors='ignore')


def _split_list(arr, sublist_size):
    # pad a list
    if len(arr) % sublist_size != 0:
        arr += [0] * (sublist_size - (len(arr) % sublist_size))
    return [arr[x:x + sublist_size] for x in range(0, len(arr), sublist_size)]


class MessageCoder:
    def encode(string):
        ...

    def decode(encoded_data):
        ...


class Base4MessageCoder(MessageCoder):
    def byte_to_dec_array(byte):
        result = [None, None, None, None]
        result[0] = (byte & 0b11000000) >> 6
        result[1] = (byte & 0b00110000) >> 4
        result[2] = (byte & 0b00001100) >> 2
        result[3] = (byte & 0b00000011)

        return result

    def dec_array_to_byte(encoded_data):
        result = 0
        result |= int(encoded_data[0]) << 6
        result |= int(encoded_data[1]) << 4
        result |= int(encoded_data[2]) << 2
        result |= int(encoded_data[3])

        return result

    def encode(msg: str):
        byte_message = bytes(msg, 'utf-8')
        arr = []
        for b in byte_message:
            arr.extend(Base4MessageCoder.byte_to_dec_array(b))

        return arr

    def decode(arr):
        chunks = _split_list(arr, 4)

        dec_list = []
        for chunk in chunks:
            dec_list.append(Base4MessageCoder.dec_array_to_byte(chunk))

        return bytes(dec_list).decode('utf-8', errors='ignore')


class Base2MessageCoder(MessageCoder):
    def encode(string):
        ascii_values = [ord(c) for c in string]

        binary_strings = [bin(av) for av in ascii_values]
        binary_strings = [b.replace('0b', '') for b in binary_strings]
        binary_strings = [b.rjust(8, '0') for b in binary_strings]

        # Create a list of the bits in each binary string
        bits = [[int(bit) for bit in b] for b in binary_strings]

        # Flatten the list of bits into a single list
        bits = [bit for sublist in bits for bit in sublist]

        return bits

    def decode(bits):
        # Split the list of bits into 8-bit chunks
        binary_strings = [bits[i:i+8] for i in range(0, len(bits), 8)]

        # Join each chunk into a single binary string
        binary_strings = ['0b' + ''.join([str(b) for b in binary_string])
                          for binary_string in binary_strings]

        # Convert each binary string to an integer
        ascii_values = [int(b, 2) for b in binary_strings]

        # Convert each integer to a character
        characters = [chr(av) for av in ascii_values]

        # Join the characters together to create a string
        string = ''.join(characters)

        return string
