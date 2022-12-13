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
    arr += [0] * (sublist_size - (len(arr) % sublist_size))
    return [arr[x:x + sublist_size] for x in range(0, len(arr), sublist_size)]
