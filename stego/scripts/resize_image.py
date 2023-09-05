from PIL import Image
import sys
from pathlib import Path

from stego import config


def resize_image_with_aspect_ratio(input_path: str, output_path: str, new_width: int) -> None:
    image = Image.open(input_path)

    original_width, original_height = image.size
    aspect_ratio = original_height / original_width
    new_height = int(new_width * aspect_ratio)

    resized_image = image.resize((new_width, new_height), Image.LANCZOS)

    resized_image.save(output_path)


def generate_output_path(input_path: str, base_dir: str, new_width: int) -> Path:

    name_with_extension = Path(input_path).name
    name = name_with_extension.split('.')[0]

    return Path(base_dir) / f"{name}_{new_width}.jpg"


if __name__ == '__main__':
    input_path = sys.argv[1]
    base_dir = Path(config.get_output_dir()) / 'resized'

    Path(base_dir).mkdir(parents=True, exist_ok=True)

    for new_width in range(600, 3000, 219):
        output_path = generate_output_path(input_path, base_dir, new_width)
        resize_image_with_aspect_ratio(input_path, output_path, new_width)
