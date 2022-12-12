import unireedsolomon as rs

coder = None


def prepare_message(msg):
    global coder
    coder = rs.RSCoder(200, len(msg))
    return coder.encode(msg)


def decode_message(retrieved_data):
    message, _ = coder.decode(retrieved_data)
    return message
