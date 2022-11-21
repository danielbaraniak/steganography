import cv2
import numpy as np


def pad_image(img: np.ndarray, block_size=8):
    padding_size = []

    for dimension in img.shape:
        padding_size.append((block_size - (dimension % block_size)) % block_size)

    img = cv2.copyMakeBorder(img, 0, padding_size[0], 0, padding_size[1], cv2.BORDER_REFLECT)
    return img


def divide_image(img: np.ndarray, block_size=8):
    h, w = img.shape
    columns = np.split(img, h // block_size, axis=0)
    blocks = [np.split(column, w // block_size, axis=1) for column in columns]

    return blocks


def stack_image(blocks):
    return np.block(blocks)
