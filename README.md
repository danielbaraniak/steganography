# Sprinters

Final project

## Instalation

1. Create and run a virtual environment

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

1. Install all requirements

    ```bash
    pip3 install -r requirements.txt
    ```

## Usage

- Embedding a message in the image

    ```bash
    python launch.py -i input_file.jpg -q 50 -m "secret message" -o output_file.jpg 
    ```
  
    where `q` is quality level. It should be possible to decode the message from the image compressed to this quality level.


- Decoding steganograpy image

    ```bash
    python launch.py -i input_file.jpg -d
    ```
    
- Launching gui

    ```bash
    python launch.py --gui
    ```

- Help
  
    ```bash
    python launch.py --help
    ```
    ```bash
    usage: launch.py [-h] [-i INPUT]
                     [--quality_level {1, ... ,100}]
                     [-m MESSAGE] [-o OUTPUT] [-d] [-g]
    
    Steganography tool.
    
    options:
      -h, --help            show this help message and exit
      -i INPUT, --input INPUT
                            Filename of the image to process
      --quality_level {1, ... ,100}
                            It should be possible to decode the message from the image compressed to this quality level.
      -m MESSAGE, --message MESSAGE
                            Message to be encoded.
      -o OUTPUT, --output OUTPUT
      -d, --decode
      -g, --gui             Launch GUI
    ```
