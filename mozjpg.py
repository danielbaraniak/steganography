import mozjpeg_lossless_optimization

with open("./image.jpg", "rb") as input_jpeg_file:
    input_jpeg_bytes = input_jpeg_file.read()

output_jpeg_bytes = mozjpeg_lossless_optimization.optimize(input_jpeg_bytes)

with open("./out.jpg", "wb") as output_jpeg_file:
    output_jpeg_file.write(output_jpeg_bytes)