from itertools import chain
from unittest import TestCase

from stego.coder.message import message_to_dec, dec_to_message, Base2MessageCoder


class TestMessage(TestCase):
    def test_encode_than_decode_even_size(self):
        message = "v89 wib fkj ghf 20"

        encoded_msg = message_to_dec(message)
        decoded_msg = dec_to_message(chain.from_iterable(encoded_msg))

        self.assertEqual(message, decoded_msg)

    def test_encode_than_decode_base2(self):
        message = "Functions creating iterators for efficient looping"

        encoded_msg = Base2MessageCoder.encode(message)
        print(f"{len(message)=}\n{len(encoded_msg)=}")
        decoded_msg = Base2MessageCoder.decode(encoded_msg)
        self.assertEqual(message, decoded_msg)
