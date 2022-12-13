import unittest
from itertools import chain

import numpy as np
import pywt

from stego.codec import embed, extract, encode_band, decode_band


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





if __name__ == '__main__':
    unittest.main()
