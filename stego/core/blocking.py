import numpy as np


def crop_image_to_divisible(img: np.ndarray, block_size: int) -> tuple[any, tuple[int, int]]:
    new_height, new_width = get_new_shape(img, block_size)
    return img[:new_height, :new_width], (new_height, new_width)


def get_new_shape(img: np.ndarray, block_size: int) -> tuple[int, int]:
    height, width = img.shape[:2]
    new_height = (height // block_size) * block_size
    new_width = (width // block_size) * block_size
    return new_height, new_width


def divide_image(img: np.ndarray, block_size: int = 8) -> list[np.ndarray]:
    height, width = img.shape[:2]
    blocks_wide = width // block_size
    blocks_high = height // block_size
    blocks = []

    for i in range(blocks_high):
        for j in range(blocks_wide):
            start_y = i * block_size
            end_y = (i + 1) * block_size
            start_x = j * block_size
            end_x = (j + 1) * block_size
            block = img[start_y:end_y, start_x:end_x]
            blocks.append(block)

    return blocks


def merge_blocks(blocks: list[np.ndarray], img_shape: tuple) -> np.ndarray:
    block_size = blocks[0].shape[0]
    blocks_wide = img_shape[1] // block_size
    blocks_high = img_shape[0] // block_size
    merged_img = np.zeros(img_shape, dtype=blocks[0].dtype)

    block_idx = 0
    for i in range(blocks_high):
        for j in range(blocks_wide):
            start_y = i * block_size
            end_y = (i + 1) * block_size
            start_x = j * block_size
            end_x = (j + 1) * block_size
            merged_img[start_y:end_y, start_x:end_x] = blocks[block_idx]
            block_idx += 1

    return merged_img


def calculate_percentile_threshold(original_img: np.ndarray,
                                   compressed_img: np.ndarray,
                                   percentile: int) -> float:
    diff = np.abs(original_img - compressed_img)
    threshold = np.percentile(diff, percentile)
    return threshold
