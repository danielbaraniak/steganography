from itertools import cycle
from stego import codec
from stego.message import message_to_dec, dec_to_message
from stego.transform.dwt import Iwt


class StegoCoder:
    def __init__(self):
        self.iwt = Iwt('haar', level=3, scale=1)

    def _loop_message(self, message):
        return cycle(message)

    def encode(self, img, message):
        self.iwt.forward(img)
        ll = self.iwt.coefficients[0]
        coefficients = self.iwt.coefficients[-1]

        msg_iterator = iter(self._loop_message(message_to_dec(message)))
        coefficients_new = [codec.encode_band(
            band, msg_iterator) for band in coefficients]

        self.iwt.coefficients[-1] = tuple(coefficients_new)

        return self.iwt.inverse()

    def decode(self, img):
        self.iwt.forward(img)
        ll = self.iwt.coefficients[0]
        coefficients = self.iwt.coefficients[-1]

        extracted_data = []

        for band in coefficients:
            extracted_data += codec.decode_band(band)

        return dec_to_message(extracted_data)
