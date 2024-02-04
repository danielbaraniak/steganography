import tomllib
from collections import namedtuple

with open('config.toml', 'rb') as f:
    config = tomllib.load(f)


def get_encoder_config() -> dict:
    return config['encoder']


def get_images_dir():
    return config['directories']['images']


def get_output_dir():
    return config['directories']['output']


def get_images_list():
    return config['images']['image_files']


def get_gui_settings():
    gui_settings = namedtuple('GuiSettings', ['zoom_in_factor', 'zoom_out_factor', 'scroll_step', 'image_formats'])
    return gui_settings(**config['gui'])
