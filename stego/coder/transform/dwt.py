from abc import ABC, abstractmethod

import numpy as np
import pywt


class Transform(ABC):
    @abstractmethod
    def forward(self, arr):
        pass

    @abstractmethod
    def inverse(self):
        pass


class Dwt(Transform):
    def __init__(self, wavelet, level=1):
        self.wavelet = wavelet
        self.level = level
        self.coefficients = None

    def forward(self, img):
        self.coefficients = pywt.wavedec2(img, wavelet=self.wavelet, level=self.level)

        return self.coefficients

    def inverse(self):
        img = pywt.waverec2(self.coefficients, wavelet=self.wavelet)
        img = np.where(img > 255, 255, img)
        img = np.where(img < 0, 0, img)
        return np.rint(img).astype(np.uint8)


class Iwt(Transform):
    def __init__(self, wavelet, level=1, scale=None):
        self.wavelet = wavelet
        self.level = level
        self.coefficients = None
        if scale:
            self.scale = scale
        else:
            self.scale = 2**level

    def forward(self, img):
        self.coefficients = pywt.wavedec2(img, wavelet=self.wavelet, level=self.level)
        self._to_int()
        return self.coefficients

    def inverse(self):
        self._inverse_to_int()
        img = pywt.waverec2(self.coefficients, wavelet=self.wavelet)
        img = np.where(img > 255, 255, img)
        img = np.where(img < 0, 0, img)
        return np.rint(img).astype(np.uint8)

    def _to_int(self):
        arr, coeff_slices = pywt.coeffs_to_array(self.coefficients)
        arr = np.rint(arr * self.scale).astype(int)
        self.coefficients = pywt.array_to_coeffs(
            arr, coeff_slices, output_format="wavedec2"
        )

    def _inverse_to_int(self):
        arr, coeff_slices = pywt.coeffs_to_array(self.coefficients)
        arr = arr / self.scale
        self.coefficients = pywt.array_to_coeffs(
            arr, coeff_slices, output_format="wavedec2"
        )
