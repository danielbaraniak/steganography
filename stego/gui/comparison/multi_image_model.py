import cv2
from PySide6.QtCore import QAbstractListModel, QModelIndex, Signal

from stego.core.utils import dwt_rgb_forward
from stego.gui.comparison.color_channel import ColorChannel


class MultiImageModel(QAbstractListModel):
    dataChanged = Signal(int)

    def __init__(self, num_images=2):
        super().__init__()
        self._images_original = [None for _ in range(num_images)]
        self._images_transformed = [None for _ in range(num_images)]

        self.color_channel = ColorChannel.RGB
        self.wavelet = "haar"
        self.level = 1
        self.detail = "ad"

    def rowCount(self, parent=QModelIndex()):
        return len(self._images_original)

    def set_image(self, index, img_array):
        self._images_original[index] = img_array
        self.dataChanged.emit(index)

    def get_image(self, i):
        image = self._images_transformed[i]
        if image is None:
            image = self._images_original[i]
            if self.color_channel == ColorChannel.RGB:
                return image
            else:
                return cv2.split(image)[self.color_channel.get_index()]

        channels = {
            ColorChannel.RED: self._images_transformed[i][0],
            ColorChannel.GREEN: self._images_transformed[i][1],
            ColorChannel.BLUE: self._images_transformed[i][2],
        }

        if self.level == 0:
            return self.get_approximation(channels)
        return self.get_transformed_image(channels)

    def get_transformed_image(self, channels: dict):
        if self.color_channel == ColorChannel.RGB:
            image_channels = [
                channels[channel][self.level][self.detail] for channel in channels
            ]
            return cv2.merge(image_channels)

        return channels[self.color_channel][self.level][self.detail]

    def get_approximation(self, channels: dict):
        if self.color_channel == ColorChannel.RGB:
            return cv2.merge([channels[channel][self.level] for channel in channels])

        return channels[self.color_channel][self.level]

    def transform_images(self, *args, **kwargs):
        if kwargs.get("level") == 0:
            self._images_transformed = [None] * len(self._images_original)
        else:
            self._images_transformed = [
                dwt_rgb_forward(img, *args, **kwargs) for img in self._images_original
            ]
        self.dataChanged.emit(-1)

    def set_channel(self, channel: ColorChannel):
        self.color_channel = channel
        self.dataChanged.emit(-1)

    def set_level(self, level: int):
        self.level = level
        self.dataChanged.emit(-1)

    def set_detail(self, detail: str):
        self.detail = detail
        self.dataChanged.emit(-1)
