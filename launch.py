#!/usr/bin/python3
import argparse
import logging.handlers

import cv2

from stego.coder.image_coder import RobustStegoCoder
from stego.coder.transform.dwt import Dwt
from stego.gui import app

LOG_FILE_PATH = "stego.log"

logging.basicConfig(filename=LOG_FILE_PATH, filemode='a', level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(description='Steganography tool.')

    # (self, transform, levels_to_encode: int = 1, quality_level=50, alpha: float = 1):
    parser.add_argument('-i', '--input', help='Filename of the image to process')
    parser.add_argument('--quality_level', '-q',
                        help='It should be possible to decode the message '
                             'from the image compressed to this quality level.',
                        type=int,
                        choices=range(1, 101),
                        default=60
                        )
    parser.add_argument('-m', '--message', help='Message to be encoded.')
    parser.add_argument('-o', '--output')
    parser.add_argument('-d', '--decode', action='store_true')
    parser.add_argument('-g', '--gui', help='Launch GUI', action='store_true')

    args = parser.parse_args()

    stego_coder = RobustStegoCoder(Dwt('haar', level=3), levels_to_encode=1, quality_level=args.quality_level, alpha=1)

    image = None

    if args.gui:
        app.run()

    if args.input is None:
        parser.error("Input file is required")
    if args.decode:
        image = cv2.imread(args.input)
        msg = stego_coder.decode_color_image(image)
        logging.info(f"Decoding '{args.input}';{msg=}")
        print(msg)
    if args.message:
        image = cv2.imread(args.input)
        image = stego_coder.encode_color_image(img=image, message=args.message)
        logging.info(f"Encoding '{args.message}' in '{args.input}'")
    if args.output:
        cv2.imwrite(args.output, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])



if __name__ == '__main__':
    main()
