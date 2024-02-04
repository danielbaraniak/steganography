#!/usr/bin/python3
import argparse
import logging.handlers
import sys

from stego.gui import app

LOG_FILE_PATH = "output/stego.log"

logging.basicConfig(filename=LOG_FILE_PATH, filemode='a', level=logging.INFO)


def main():
    if len(sys.argv) == 1:
        sys.exit(app.run())

    parser = argparse.ArgumentParser(description='Steganography tool.')

    parser.add_argument('-g', '--gui', help='Launch GUI', action='store_true')

    args = parser.parse_args()

    if args.gui:
        sys.exit(app.run())


if __name__ == '__main__':
    main()
