from PIL import Image
import sys
import os

def resize_image_with_aspect_ratio(input_path, output_path, new_width):
    # Open the image
    image = Image.open(input_path)

    # Calculate the new height while maintaining the aspect ratio
    original_width, original_height = image.size
    aspect_ratio = original_height / original_width
    new_height = int(new_width * aspect_ratio)

    # Resize the image
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)

    absolute_path = os.path.abspath(output_path)
    print(absolute_path)

    # Save the resized image
    resized_image.save(output_path)


if __name__ == '__main__':
    # get the input and output path from the command line
    input_path = sys.argv[1]

    for new_width in range(600, 3000, 219):
        name_with_extension = input_path.split('/')[-1]
        name = name_with_extension.split('.')[0]
        output_path = f'./images/resized/{name}_{new_width}.jpg'
        resize_image_with_aspect_ratio(input_path, output_path, new_width)