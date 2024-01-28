from CM4_MBUS_LIB import *
from datetime import datetime
from time import sleep
from PIL import Image

def image_to_register_array(image_path):
    try:
        # Open the image
        img = Image.open(image_path)

        # Convert image to 1-bit mode (monochrome)
        img = img.convert('1')

        # Get pixel values as a flat list
        pixel_values = list(img.getdata())

        # Reshape the flat list into rows and columns
        width, _height = img.size
        binary_array = [pixel_values[i:i + width] for i in range(0, len(pixel_values), width)]

        for i in range(0, len(binary_array)):
            for j in range(0, len(binary_array[i])):
                binary_array[i][j] = 1 if binary_array[i][j] == 0 else 0
        registers_array = []
        for i in range(0, len(binary_array)):
            row = []
            row.append(i)
            for r in range(0, len(binary_array[i]), 16):
                value = 0
                for j in range(0, 16):
                    value = value | (binary_array[i][r+j]<<15-j)
                row.append(value)
            registers_array.append(row)
        
        return registers_array

    except Exception as e:
        print(f"Error: {e}")
        return None

image_path = 'mchtr.jpg'
registers_array = image_to_register_array(image_path)
master = RS485_RTU_Master(1)
master.write_multiple_holding_registers(1, int(0x49), [1])
sleep(0.5)

for i in range(0, len(registers_array)):
    data = registers_array[i]
    try:
        master.write_multiple_holding_registers(1, int(0x4A), data)
    except Transmission_Exception:
        sleep(0.2)
        try:
            master.write_multiple_holding_registers(1, int(0x4A), data)
        except Transmission_Exception:
            sleep(0.5)
            master.write_multiple_holding_registers(1, int(0x4A), data)
    sleep(0.1)


    
