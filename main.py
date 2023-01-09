#!/usr/bin/env python3

import cv2
import numpy as np
from stego.image_coder import StegoCoder

import stego.message
from stego import correction_codes
from stego.message import message_to_dec
from stego.transform.dwt import Iwt

PATH = "images/2.jpg"
MESSAGE = "Osadzenie w 3 poziomie"


def encode(img: np.ndarray, message: str):
    coder = StegoCoder()

    data = message_to_dec(message)
    message_iterator = iter(data)

    iwt = Iwt('haar', level=3, scale=1)
    iwt.forward(img)


def main():
    img = cv2.imread(PATH)

    rs_message = correction_codes.prepare_message(MESSAGE)
    data = stego.message.message_to_dec(rs_message)

    coder = StegoCoder()

    stego_img = coder.encode(img, data)


if __name__ == "__main__":
    main()
