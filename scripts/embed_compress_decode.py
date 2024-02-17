import itertools
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from time import time

import cv2
from pqdm.processes import pqdm

from scripts import utils
from stego.core import message as msg_utils
from stego import config
from stego.core import metrics
from stego.core.errors import CapacityError

SECRET = "Lorem ipsum dolor sit amet"


def encode_compress_decode(encoder_config, img_dir_path, file_name):
    img_path = img_dir_path + file_name
    img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)

    info = defaultdict(int)
    info["file_name"] = file_name
    info |= encoder_config
    try:
        original, stego_image, msg_raw = utils.embed(img, SECRET, encoder_config)
    except CapacityError:
        return info

    decoded_results = {}

    ecc_message_original = msg_utils.encode_ecc(
        SECRET.encode("ASCII"), **encoder_config
    )
    for quality in [95, 75, 55]:
        compressed_image = utils.compress_image(stego_image, quality)
        message, ecc_message, message_raw_decoded = utils.decode(
            compressed_image, encoder_config
        )
        correct_bits = utils.calculate_accuracy(msg_raw, message_raw_decoded)
        correct_bytes_count = sum(
            1
            for msg, msg_decoded in zip(ecc_message_original, ecc_message)
            if msg == msg_decoded
        )
        is_success = message == SECRET
        is_false_positive = message is not None and message != SECRET

        decoded_results[f"{quality}_correct_bits"] = correct_bits
        decoded_results[f"{quality}_correct_bytes"] = correct_bytes_count / len(
            ecc_message_original
        )
        decoded_results[f"{quality}_is_success"] = is_success
        decoded_results[f"{quality}_is_false_positive"] = is_false_positive

    info |= metrics.diff_metrics(original, stego_image)

    info |= decoded_results

    return info


def main():
    encoder_config = config.get_encoder_config()

    output_dir = Path(config.get_output_dir()) / "test"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    img_dir_path = config.get_images_dir()
    file_names = config.get_images_list()

    args = []

    # for (
    #     alpha,
    #     ecc_symbols,
    #     level,
    #     block_size,
    #     color_space,
    #     use_channels,
    #     coefficients,
    #     file_name,
    # ) in itertools.product(
    #     [1, 2],
    #     [1, 5, 12],
    #     [3, 4, 5],
    #     [3, 5],
    #     ["RGB", "YCrCb"],
    #     [[0], [1], [2], [0, 1, 2]],
    #     [["ad"], ["da"], ["dd"]],
    #     file_names,
    # ):
    #     custom_config = {
    #         "alpha": alpha,
    #         "ecc_symbols": ecc_symbols,
    #         "level": level,
    #         "block_size": block_size,
    #         "use_channels": use_channels,
    #         "color_space": color_space,
    #         "coefficients": coefficients,
    #     }
    #
    #     parameters = encoder_config.copy()
    #     parameters |= custom_config
    #     args.append([parameters, img_dir_path, file_name])

    for (
        alpha,
        ecc_symbols,
        level,
        block_size,
        color_space,
        use_channels,
        coefficients,
        file_name,
    ) in itertools.product(
        [2], [6], [5], [3], ["YCrCb"], [[0]], [["da", "ad", "dd"]], file_names[3:6]
    ):
        custom_config = {
            "alpha": alpha,
            "ecc_symbols": ecc_symbols,
            "level": level,
            "block_size": block_size,
            "use_channels": use_channels,
            "color_space": color_space,
            "coefficients": coefficients,
        }

        parameters = encoder_config.copy()
        parameters |= custom_config
        args.append([parameters, img_dir_path, file_name])

    results = pqdm(args, encode_compress_decode, n_jobs=1, argument_type="args")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    utils.save_data_to_csv(
        results, str(output_dir / f"encode_modify_decode_{timestamp}.csv")
    )


if __name__ == "__main__":
    start_time = time()
    main()
    end_time = time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time:.2f} seconds")
