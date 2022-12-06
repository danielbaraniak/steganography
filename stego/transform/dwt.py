from abc import ABC, abstractmethod
from typing import Self

import numpy as np
import pywt


class Transform(ABC):
    @abstractmethod
    def forward(self):
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


class Iwt(Dwt):
    def __init__(self, wavelet, mode='symmetric', axes=(-2, -1), scale=2) -> Self:
        super().__init__(wavelet, mode, axes)
        self.scale = scale

    def forward(self, img):
        coeffs = super().forward(img)
        ll, (lh, hl, hh) = coeffs
        arr = np.array([ll, lh, hl, hh])
        arr = np.rint(arr * self.scale).astype(int)
        self.coeffs = [arr[0], [arr[1], arr[2], arr[3]]]
        return self.coeffs

    def inverse(self):
        ll, (lh, hl, hh) = self.coeffs
        arr = np.array([ll, lh, hl, hh])
        arr = (arr / self.scale)
        self.coeffs = [arr[0], [arr[1], arr[2], arr[3]]]
        return super().inverse()
