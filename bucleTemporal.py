import serial
import crcmod
import binascii
from binascii import unhexlify
from serial import SerialException
import random
import time

def s1c_ESN(s1cport):
    try:
        ser = serial.Serial(
            port=s1cport,
            timeout=5,  
            baudrate=9600,
            bytesize=8,
            parity='N',
            stopbits=2,
            xonxoff=False
        )

        array = 'aa0501'

        if ser.isOpen():
            print("S1C port opened")

        print("COMANDO GET ID")

        crc16_func = crcmod.mkCrcFun(0x11021, initCrc=0x0000, xorOut=0xffff)
        command = bytearray.fromhex(array)
        result = hex(crc16_func(command))
        crc_1 = unhexlify(result[2:4])
        crc_2 = unhexlify(result[4:6])
        command.extend(crc_2 + crc_1)

        ser.write(command)

        x = ser.read(256)
        response = x.hex()

        if response:
            print("ESN Received:", response)

            if response.startswith("aa"):
                length = int(response[2:4], 16)
                command_id = response[4:6]
                esn_hex = response[6:-4]  
                crc_received = response[-4:]
                esn_decimal = int(esn_hex, 16)
                esn_formatted = f"0-{esn_decimal}"

                #print(f"Length: {length}")
                #print(f"Command ID: {command_id}")
                #print(f"ESN (Hex): {esn_hex}")
                #print(f"ESN (Decimal): {esn_decimal}")
                print(f"ESN (Formatted): {esn_formatted}")
                #print(f"CRC Received: {crc_received}")

        else:
            print("No response received")

        ser.close()
        return response

    except SerialException as e:
        print(f"ERROR: {e}")

def s1c_send_data(user_data, s1cport, msg_type):
    try:
        ser = serial.Serial(port=s1cport, timeout=3, baudrate=9600, bytesize=8,
                            parity='N', stopbits=2, xonxoff=False)

        datatobesend = user_data.encode('utf-8').hex()

        if msg_type == "truncated":
            cmd = "26"
            max_data_len = 47
        elif msg_type == "raw":
            cmd = "27"
            max_data_len = 53
        else:
            print("Tipo de mensaje no válido")
            return

        data_len = len(datatobesend) // 2
        if data_len > max_data_len:
            print(f"Los datos de usuario no pueden exceder {max_data_len} bytes")
            return

        length = format(5 + data_len, '02x')
        array = f'aa{length}{cmd}{datatobesend}'

        if ser.isOpen():
            print("S1C port opened")

        print(f"COMANDO GET {msg_type.upper()} DATA")
        crc16_func = crcmod.mkCrcFun(0x11021, initCrc=0x0000, xorOut=0xffff)
        command = bytearray.fromhex(array)
        result = hex(crc16_func(command))
        crc_1 = unhexlify(result[2:4])
        crc_2 = unhexlify(result[4:6])
        command.extend(crc_2 + crc_1)

        ser.write(command)
        x = ser.read(256)
        response = x.hex()

        if response:
            print("Dato", array)
            print("Respuesta", response)

        ser.close()
        return response
    except SerialException:
        print("ERROR ENVIAR DATA")

def generate_random_user_data():
    first_two_chars = f"{random.randint(1, 10):02d}"
    remaining_chars = f"{random.uniform(-1, 10):.4f}"[:6]
    return first_two_chars + remaining_chars + "##"

def main():
    s1cport = '/dev/ttyUSB0'
    

    while True:

        user_data = generate_random_user_data()
        esn_response = s1c_ESN(s1cport)
        print(f"Sending user data: {user_data}")
        response = s1c_send_data(user_data, s1cport, "raw")
        #print(f"Response: {response}")

        print("Waiting for 30 minutes...")
        time.sleep(15)

if __name__ == "__main__":
    main()
