from unittest import TestCase

import numpy as np
import pywt

from stego.transform.dwt import Iwt


class TestIwt(TestCase):
    def test_forward_than_inverse(self):
        image = pywt.data.camera()
        iwt = Iwt('haar', level=3)
        iwt.forward(image)
        result = iwt.inverse()

        self.assertTrue(np.allclose(image, result))
