#!/usr/bin/env python3

import cv2
from encoder import encode, decode
from metrics import mse
import unireedsolomon as rs

PATH = "images/2.jpg"
ALPHA = 0.001


def main():
    cover_img = cv2.imread(PATH, cv2.IMREAD_GRAYSCALE)

    coder = rs.RSCoder(20, 13)
    c = coder.encode("Hello, world!", return_string=False)
    print(c)

    img_encoded = encode(cover_img, c, alpha=ALPHA)

    print(cv2.PSNR(cover_img, img_encoded))

    print(mse(cover_img, img_encoded))

    cv2.imshow("stacked", img_encoded)
    cv2.waitKey(0)

    m = decode(img_encoded, cover_img, alpha=ALPHA)
    print(f"{m=}")
    print(coder.decode(m[:20]))

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
