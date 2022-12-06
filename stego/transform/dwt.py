from abc import ABC, abstractmethod
from typing import Self

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
    def __init__(self, wavelet, mode='symmetric', axes=(-2, -1)) -> Self:
        super().__init__()
        self.coeffs = None
        self.wavelet = wavelet
        self.mode = mode
        self.axes = axes

    def forward(self, img):
        coeffs = pywt.dwt2(data=img, wavelet=self.wavelet,
                           mode=self.mode, axes=self.axes)
        self.coeffs = coeffs
        return coeffs

    def inverse(self):
        return pywt.idwt2(coeffs=self.coeffs, wavelet=self.wavelet, mode=self.mode, axes=self.axes)


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

    def inverse(self):
        self._inverse_to_int()
        return pywt.waverec2(self.coefficients, wavelet=self.wavelet)

    def _to_int(self):
        arr, coeff_slices = pywt.coeffs_to_array(self.coefficients)
        arr = np.rint(arr * self.scale).astype(int)
        self.coefficients = pywt.array_to_coeffs(arr, coeff_slices, output_format='wavedec2')

    def _inverse_to_int(self):
        arr, coeff_slices = pywt.coeffs_to_array(self.coefficients)
        arr = (arr / self.scale)
        self.coefficients = pywt.array_to_coeffs(arr, coeff_slices, output_format='wavedec2')
