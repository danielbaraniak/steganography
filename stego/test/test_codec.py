import unittest
from itertools import chain

import numpy as np
import pywt

from stego.coder.mdle_coder import embed, extract, encode_band, decode_band
from stego.coder.message import message_to_dec, dec_to_message
from stego.coder.transform.dwt import Iwt


class TestsCodec(unittest.TestCase):
    def test_embed_than_extract(self):
        block = np.array([[175, 247, 97],
                          [124, 198, 215],
                          [98, 42, 15]])

        original_data = [3, 1, 2, 2, 0, 1, 3, 0]

        encoded_block = embed(block, original_data)
        extracted_data = extract(encoded_block)

        for x, y in zip(original_data, extracted_data):
            self.assertEqual(x, y)

    def test_embed_than_extract_band(self):
        image = pywt.data.camera()

        original_data = [[3, 1, 2, 2, 0, 1, 3, 1],
                         [2, 2, 3, 0, 2, 0, 1, 3],
                         [3, 0, 1, 3, 3, 2, 0, 1]]

        encoded_img = encode_band(image, iter(original_data))
        extracted_data = decode_band(encoded_img)

        expected = chain.from_iterable(original_data)
        for x, y in zip(expected, extracted_data):
            self.assertEqual(x, y)

    def test_encode_band_keep_dims(self):
        image = pywt.data.camera()

        original_data = [[3, 1, 2, 2, 0, 1, 3, 1],
                         [2, 2, 3, 0, 2, 0, 1, 3],
                         [3, 0, 1, 3, 3, 2, 0, 1]]

        encoded_img = encode_band(image, iter(original_data))
        self.assertEqual(image.shape, encoded_img.shape)

    def test_integration_without_reverse_transform(self):
        message = "v89 wib fkj ghf 20"
        image = pywt.data.camera()
        iwt = Iwt('haar', level=1)
        iwt.forward(image)

        ll = iwt.coefficients[0]
        encoded_msg = message_to_dec(message)

        encoded_ll = encode_band(ll, iter(encoded_msg))
        extracted_data_ll = decode_band(encoded_ll)
        extracted_message = dec_to_message(extracted_data_ll)

        self.assertEqual(message[:16], extracted_message[:16])


if __name__ == '__main__':
    unittest.main()
