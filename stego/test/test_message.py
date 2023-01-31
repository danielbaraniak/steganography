from itertools import chain
from unittest import TestCase

from stego.coder.message import Base4MessageCoder


class TestMessage(TestCase):
    def test_encode_than_decode_even_size(self):
        message = "v89 wib fkj ghf 20"

        encoded_msg = Base4MessageCoder.encode(message)
        decoded_msg = Base4MessageCoder.decode(chain.from_iterable(encoded_msg))
        print(decoded_msg)
        self.assertEqual(message, decoded_msg)
