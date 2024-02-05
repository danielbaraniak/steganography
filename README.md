# Image watermarking on selected social media platforms

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Description

This project is a part of the final project for the thesis "Image watermarking on selected social media platforms". The goal of the project is to create a tool that will allow to watermark images before posting them on selected social media platforms. The tool will be able to embed a message in the image and decode it. The tool will also have a graphical user interface.



## Prerequisites

- Python 3.11 installed on your system. If you do not have Python 3.11, visit the [official Python website](https://www.python.org/downloads/) to download and install it.

## Installation Instructions

### Setting Up a Virtual Environment



It's recommended to use a virtual environment for Python projects to manage dependencies efficiently. Here's how you can set up a virtual environment for this project:

1. Open your terminal or command prompt in a root folder of the project.
2. Navigate to the project directory:
   ```sh
   cd path/to/project
   ```
3. Create a virtual environment named `venv` (or any other name you prefer):
   ```sh
   python -m venv venv
   ```
4. Activate the virtual environment:
   - On Windows:
     ```cmd
     .\venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```sh
     source venv/bin/activate
     ```

### Installing Dependencies

After setting up and activating the virtual environment, install the project dependencies by running:

```sh
python -m pip install -r requirements.txt
```

This command reads the `requirements.txt` file in your project directory and installs all the required Python packages listed there.

## Usage

### Configuration

The application can be customized through a configuration file. Below is the structure of the configuration file with descriptions for each setting:

```toml
[encoder]
alpha = 1                           # Opacity level of the watermark. Range: 0-1.
block_size = 3                      # Size of the blocks used for embedding the watermark.
level = 2                           # Level of wavelet transformation.
wavelet = "haar"                    # Type of wavelet used for transformation.
coefficients = ["ad", "da", "dd"]   # Wavelet coefficients used for embedding.
color_space = "YCrCb"               # Color space used for watermarking.
use_channels = [1, 2]               # Channels of the color space used for watermarking.
ecc_symbols = 10                    # Number of error correction symbols added to the watermark.

[gui]
zoom_in_factor = 1.25               # Factor for zooming in the image.
zoom_out_factor = 0.8               # Factor for zooming out the image.
scroll_step = 0.5                   # Step size for scrolling through the image.
image_formats = "Images (*.png *.jpg *.jpeg *.bmp)" # Supported image formats for GUI operations.
```


### Running the GUI Application

To use the tool, run the `launch.py` script from the root directory of the project:

```sh
python launch.py
```

### Testing the Application

> To facilitate imports from the `stego` when testing the project,
> you'll need to add it to your `PYTHONPATH`. 
> Look at the section [Setting PYTHONPATH for the Project](#setting-pythonpath-for-the-project) 
> for instructions on how to do that.

In the `scripts` directory, you can find scripts for batch testing the watermarking and decoding functionality. 
To run the test, execute a file from the script's directory:

```sh
python ./embed_batch.py
```

You may want to configure the input and output directories, as well as other parameters, in the config or in the script file.

#### Setting PYTHONPATH for the Project

Commands below appends the project directory to your `PYTHONPATH` for the duration of the terminal session.

Execute the commands below from the root directory of the project:
##### Unix-like Shells (bash/sh)

```sh
export PYTHONPATH=$(pwd):$PYTHONPATH
```

##### Windows Command Prompt

```cmd
set PYTHONPATH=%CD%;%PYTHONPATH%
```

##### Windows PowerShell

```powershell
$env:PYTHONPATH = "$(Get-Location);$env:PYTHONPATH"
```
