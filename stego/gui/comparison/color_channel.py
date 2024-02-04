from enum import Enum


class ColorChannel(Enum):
    RGB = "RGB"
    RED = "Red"
    GREEN = "Green"
    BLUE = "Blue"

    def get_index(self):
        return {
            ColorChannel.RGB: -1,
            ColorChannel.RED: 0,
            ColorChannel.GREEN: 1,
            ColorChannel.BLUE: 2,
        }[self]
