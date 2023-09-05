import tomllib

with open('config.toml', 'rb') as f:
    config = tomllib.load(f)


def get_encoder_config():
    return config['encoder']


def get_images_dir():
    return config['directories']['images']


def get_output_dir():
    return config['directories']['output']


def get_images_list():
    return config['images']['image_files']
