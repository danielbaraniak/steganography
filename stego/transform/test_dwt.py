from unittest import TestCase

import numpy as np
import pywt

from stego.transform.dwt import Iwt, Dwt


class TestIwt(TestCase):
    def test_forward_than_inverse(self):
        image = pywt.data.camera()
        iwt = Iwt('haar', level=3)
        iwt.forward(image)
        result = iwt.inverse()

        self.assertTrue(np.allclose(image, result))

    def test_forward_modify_inverse(self):
        image = pywt.data.camera()
        iwt = Iwt('haar', level=3)
        iwt.forward(image)

        lh = iwt.coefficients[0].copy()
        lh_m = lh + 40
        iwt.coefficients[0] = lh_m
        self.assertTrue(np.allclose(lh_m, iwt.coefficients[0]))

        modified = iwt.inverse()

        self.assertFalse(np.allclose(image, modified))

        iwt = Iwt('haar', level=3)
        iwt.forward(modified)

        lh_new = iwt.coefficients[0].copy()

        self.assertTrue(np.allclose(lh_m, lh_new))


class TestDwt(TestCase):
    def test_forward_than_inverse(self):
        image = pywt.data.camera()
        transform = Dwt('haar', level=3)
        transform.forward(image)
        result = transform.inverse()
        self.assertTrue(np.allclose(image, result))
