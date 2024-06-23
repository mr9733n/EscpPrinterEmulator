import sys
from escpos.printer import Dummy
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
import io

def generate_barcode(data, barcode_type='code128'):
    barcodes = {
        'code128': barcode.Code128,
        'ean13': barcode.EAN13,
        'ean8': barcode.EAN8
    }
    if barcode_type in barcodes:
        EAN = barcodes[barcode_type]
        ean = EAN(data, writer=ImageWriter())
        buffer = io.BytesIO()
        ean.write(buffer)
        buffer.seek(0)
        return Image.open(buffer)
    else:
        raise ValueError("Unsupported barcode type")

def interpret_esc_p_commands(byte_data):
    width, height = 800, 1200  # Увеличиваем размеры изображения
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except IOError:
        font = ImageFont.load_default()

    x, y = 10, 10
    i = 0
    while i < len(byte_data):
        byte = byte_data[i]
        if byte == 27:  # ESC
            if i + 1 < len(byte_data):
                next_byte = byte_data[i + 1]
                if next_byte == 64:  # ESC @ - инициализация принтера
                    i += 2
                elif next_byte == 69:  # ESC E - включить выделение
                    i += 2
                elif next_byte == 5:  # ESC E - выключить выделение
                    i += 2
                elif next_byte == 97:  # ESC a - выравнивание
                    if i + 2 < len(byte_data):
                        i += 3
                    else:
                        break
                elif next_byte == 107:  # ESC k - печать штрих-кода
                    if i + 4 < len(byte_data):
                        barcode_type = byte_data[i + 2]
                        barcode_data_length = byte_data[i + 3]
                        if i + 4 + barcode_data_length <= len(byte_data):
                            barcode_data = byte_data[i + 4:i + 4 + barcode_data_length].decode('ascii')
                            barcode_img = generate_barcode(barcode_data)
                            img.paste(barcode_img, (x, y))
                            y += barcode_img.height + 10
                            i += 4 + barcode_data_length
                        else:
                            break
                    else:
                        break
                elif next_byte == 105:  # ESC i - команда для работы с баркодами
                    if i + 2 < len(byte_data):
                        barcode_start = i + 2
                        while i < len(byte_data) and byte_data[i] != 27:
                            i += 1
                        barcode_data = byte_data[barcode_start:i].decode('ascii').strip()
                        if barcode_data:
                            barcode_img = generate_barcode(barcode_data, 'code128')
                            img.paste(barcode_img, (x, y))
                            y += barcode_img.height + 10
                        i += 1
                    else:
                        break
                elif next_byte == 73:  # ESC I
                    if i + 2 < len(byte_data):
                        i += 2
                    else:
                        break
                elif next_byte == 83:  # ESC S
                    if i + 2 < len(byte_data) and byte_data[i + 2] == 79:  # ESC SOH
                        i += 3
                    else:
                        i += 2
                elif next_byte == 88:  # ESC X
                    if i + 2 < len(byte_data):
                        i += 3
                    else:
                        break
                else:
                    i += 2
            else:
                break
        elif byte == 10:  # LF - перевод строки
            x = 10
            y += 20
            i += 1
        elif byte == 9:  # HT - горизонтальная табуляция
            x += 50
            i += 1
        else:
            text = chr(byte) if 32 <= byte <= 126 else '?'
            draw.text((x, y), text, font=font, fill='black')
            x += 10
            if x > width - 20:  # Перенос строки
                x = 10
                y += 20
            i += 1

    return img

def emulate_escp(file_path, output_image_path):
    printer = Dummy()

    with open(file_path, 'rb') as file:
        esc_p_string = file.read()

    printer._raw(esc_p_string)

    byte_data = printer.output

    img = interpret_esc_p_commands(byte_data)

    img.save(output_image_path)
    print(f"Emulated ESC/P output saved to {output_image_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python escp_emulator.py <path_to_input_file> <path_to_output_image>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    output_image_path = sys.argv[2]
    emulate_escp(input_file_path, output_image_path)