# ESC/P Emulator

This project is an ESC/P (Epson Standard Code for Printers) emulator that reads a text file containing ESC/P commands and generates an image file representing the printed output. The emulator handles text, barcode generation, and various ESC/P commands.

## Features

- Emulates ESC/P commands
- Generates barcodes (Code128, EAN13, EAN8)
- Handles text formatting and alignment
- Outputs the result as an image

## Requirements

- Python 3.x
- `escpos` library
- `Pillow` library
- `python-barcode` library

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/mr9733n/EscpPrinterEmulator.git
    cd escp-emulator
    ```

2. Install the required libraries:
    ```sh
    pip install python-escpos Pillow python-barcode
    ```

## Usage

To use the emulator, run the `escp_emulator.py` script with the path to the input text file and the desired output image file:

```sh
python3 escp_emulator.py input.txt output.png
```

## Example 

An example input file (input.txt):

```
ESC@ESCiLESC(cABCESCX24ESCk0ESCEESC5ESC-1ESCa1ESCHello World
ESCi0r1h200w03z02ESCa1B123456789\
ESCiC
```

## Handling Errors

The script handles errors such as missing input files. If you run the script without specifying the input and output files, it will prompt you with the correct usage message.

Example of running the script without arguments:
