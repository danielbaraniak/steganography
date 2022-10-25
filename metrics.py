from math import log10, sqrt
import numpy as np


def mse(original, compressed):
    return np.mean((original - compressed) ** 2)
