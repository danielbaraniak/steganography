from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from stego import config


def generate_noise_image(width, height):
    """Generate a random noise image with given dimensions."""
    noise_image_data = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    noise_image = Image.fromarray(noise_image_data)
    return noise_image


def scale_image(image, max_dimension=2048, interpolation=cv2.INTER_CUBIC):
    """Scale the image uniformly so that its longer dimension is max_dimension."""
    width, height = image.size

    # Determine the scaling factor
    if width > height:
        scaling_factor = max_dimension / width
    else:
        scaling_factor = max_dimension / height

    new_width = int(width * scaling_factor)
    new_height = int(height * scaling_factor)

    return cv2.resize(convert_to_cv2(image), (new_width, new_height), interpolation)


def convert_to_cv2(image):
    open_cv_image = np.array(image)
    return cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)


if __name__ == "__main__":
    base_dir = Path(config.get_output_dir()) / "resampling"
    Path(base_dir).mkdir(parents=True, exist_ok=True)

    image_sizes = [(3000, 4000), (2000, 2000), (1024, 2024)]
    interpolation_methods = [(cv2.INTER_LANCZOS4, "lanczos4")]

    for size in image_sizes:
        original_image = generate_noise_image(*size)
        output_path = base_dir / f"original_{size[0]}x{size[1]}.jpg"
        original_image.save(str(output_path), quality=100)

        for method, method_name in interpolation_methods:
            scaled_image = scale_image(original_image, interpolation=method)
            output_path = base_dir / f"scaled_{size[0]}x{size[1]}_{method_name}.jpg"
            cv2.imwrite(str(output_path), scaled_image, [cv2.IMWRITE_JPEG_QUALITY, 100])
