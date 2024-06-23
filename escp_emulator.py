import sys
import os
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
import io

def generate_barcode(data, code_type='code128'):
    if code_type.lower() == 'code128':
        barcode_class = barcode.get_barcode_class('code128')
    else:
        raise ValueError("Unsupported barcode type")
    
    barcode_instance = barcode_class(data, writer=ImageWriter())
    buffer = io.BytesIO()
    barcode_instance.write(buffer)
    buffer.seek(0)
    return Image.open(buffer)

def interpret_esc_p_commands(byte_data):
    img = Image.new('RGB', (600, 600), color='white')
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    x, y = 10, 10
    i = 0
    while i < len(byte_data):
        byte = byte_data[i]
        if byte == 27:  # ESC
            i += 1
            if i < len(byte_data):
                command = byte_data[i]
                # Handle sequence 0x1B, 0x35, 0x1B, 0x2D, 0x31, 0x1B, 0x61, 0x31, 0x1B, 0x20, 0x31
                if byte_data[i:i+11] == [27, 53, 27, 45, 49, 27, 97, 49, 27, 32, 49]:
                    i += 11
                    text_data = ""
                    while i < len(byte_data) and byte_data[i] != 27:
                        text_data += chr(byte_data[i])
                        i += 1
                    if text_data:
                        draw.text((x, y), text_data, font=font, fill='black')
                        y += 20
                        x = 10
                elif command == 105:  # 'i' for barcode
                    i += 1
                    barcode_settings = ""
                    while i < len(byte_data) and byte_data[i] != 66:
                        barcode_settings += chr(byte_data[i])
                        i += 1
                    i += 1  # Skip 'B'
                    barcode_data = ""
                    while i < len(byte_data) and byte_data[i] != 27 and byte_data[i] != 10 and byte_data[i] != 13:
                        barcode_data += chr(byte_data[i])
                        i += 1
                    if barcode_data:
                        try:
                            barcode_data = barcode_data.strip('\\')  # Remove trailing backslashes
                            print(f"Generating barcode with data: {barcode_data}")
                            barcode_img = generate_barcode(barcode_data.strip(), 'code128')
                            img.paste(barcode_img, (x, y))
                            y += barcode_img.height + 10
                        except Exception as e:
                            print(f"Error generating barcode: {e}, Data: {barcode_data}")
                elif command == 69:  # 'E' for bold text
                    i += 1
                    text_data = ""
                    while i < len(byte_data) and byte_data[i] != 27 and byte_data[i] != 10 and byte_data[i] != 13:
                        text_data += chr(byte_data[i])
                        i += 1
                    if text_data:
                        draw.text((x, y), text_data, font=font, fill='black')
                        y += 20
                        x = 10
                elif command in [10, 13]:  # LF or CR
                    x = 10
                    y += 20
                    i += 1
                    continue
        elif byte == 10:  # LF
            x = 10
            y += 20
            i += 1
        else:
            text = chr(byte) if 32 <= byte <= 126 else '?'
            draw.text((x, y), text, font=font, fill='black')
            x += 10
            if x > img.width - 10:
                x = 10
                y += 20
            i += 1

    return img

def emulate_escp(input_file_path, output_image_path):
    if not os.path.exists(input_file_path):
        print(f"Error: Input file '{input_file_path}' not found.")
        return

    with open(input_file_path, 'rb') as file:
        byte_data = file.read()

    img = interpret_esc_p_commands(byte_data)
    img.save(output_image_path)
    print(f"Emulated ESC/P output saved to {output_image_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python escp_emulator.py <input_file> <output_image>")
    else:
        input_file_path = sys.argv[1]
        output_image_path = sys.argv[2]
        emulate_escp(input_file_path, output_image_path)