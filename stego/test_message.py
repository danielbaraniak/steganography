from itertools import chain
from unittest import TestCase

from stego.message import message_to_dec, dec_to_message


class TestMessage(TestCase):
    def test_encode_than_decode_even_size(self):
        message = "v89 wib fkj ghf 20"

        encoded_msg = message_to_dec(message)
        decoded_msg = dec_to_message(chain.from_iterable(encoded_msg))

        self.assertEqual(message, decoded_msg)


