import cv2
import numpy as np


def pad_image(img: np.ndarray, block_size=8):
    padding_size = []

    for dimension in img.shape:
        padding_size.append(
            (block_size - (dimension % block_size)) % block_size)

    img = cv2.copyMakeBorder(
        img, 0, padding_size[0], 0, padding_size[1], cv2.BORDER_REFLECT)
    return img


def perfect_divide_image(img: np.ndarray, block_size=8):
    h, w = img.shape
    columns = np.split(img, h // block_size, axis=0)
    blocks = [np.split(column, w // block_size, axis=1) for column in columns]

    return blocks


def stack_image(blocks):
    return np.block(blocks)


def crop_to_fit(img: np.ndarray, block_size):
    new_size = []
    for dimension in img.shape:
        new_size.append(
            dimension - (dimension % block_size)
        )

    return img[:new_size[0], :new_size[1]]


def divide_image(img: np.ndarray, block_size=8):
    new_img = crop_to_fit(img, block_size)

    h, w = img.shape
    columns = np.split(new_img, h // block_size, axis=0)
    blocks = [np.split(column, w // block_size, axis=1) for column in columns]

    return blocks


class CropBlocker:
    def __init__(self, img: np.ndarray):
        self.img: np.ndarray = img

    def divide(self, block_size=8):
        new_img = crop_to_fit(self.img, block_size)

        h, w = self.img.shape
        columns = np.split(new_img, h // block_size, axis=0)
        blocks = [np.split(column, w // block_size, axis=1) for column in columns]

        return blocks

    def stack(self, blocks):
        stacked = np.block(blocks)
        image = self.img.copy()
        h, w = stacked.shape
        image[:h, :w] = stacked
        return image


