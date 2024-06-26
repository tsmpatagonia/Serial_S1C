import crcmod
import os.path
import sys
import platform
import time
import serial
from time import sleep
import crcmod  # sudo pip install crcmod
import binascii
from binascii import unhexlify
import logging
from datetime import datetime
from collections import defaultdict
from serial import SerialException
from random import randrange
import json
from random import randint
import os


def s1c_ESN(s1cport):
    try:
        # Configuración de la conexión serial
        ser = serial.Serial(
            port=s1cport,
            timeout=3,
            baudrate=9600,
            bytesize=8,
            parity='N',
            stopbits=2,
            xonxoff=False
        )

        # Comando para obtener el ESN
        array = 'aa0501'
        time.sleep(3)

        if ser.isOpen():
            print("S1C port opened")

        print("COMANDO GET ID")
        time.sleep(5)

        # Crear función CRC-16 con el polinomio especificado
        crc16_func = crcmod.mkCrcFun(0x11021, initCrc=0x0000, xorOut=0xffff)

        # Convertir el comando a bytearray
        command = bytearray.fromhex(array)

        # Generar CRC basado en el comando dado
        result = hex(crc16_func(command))
        crc_1 = unhexlify(result[2:4])
        crc_2 = unhexlify(result[4:6])

        # Añadir CRC al comando
        command.extend(crc_2 + crc_1)

        # Escribir el comando en el puerto serial
        ser.write(command)

        # Leer la respuesta
        x = ser.read(256)
        print(x)
        response = x.hex()

        if response:
            print("ESN Received:", response)

            # Decodificar la respuesta
            if response.startswith("aa"):
                length = int(response[2:4], 16)
                command_id = response[4:6]
                # Asumiendo que los últimos 4 caracteres son el CRC
                esn = response[6:-4]
                crc_received = response[-4:]

                print(f"Length: {length}")
                print(f"Command ID: {command_id}")
                print(f"ESN: {esn}")
                print(f"CRC Received: {crc_received}")

        # Cerrar la conexión serial
        ser.close()

        return response

    except SerialException as e:
        print(f"ERROR: {e}")




def s1c_send_data(datatobesend, s1cport):
    try:
        ser = serial.Serial(port=s1cport, timeout=3, baudrate=9600, bytesize=8,
                            parity='N', stopbits=2, xonxoff=False)  # Serial connect port number
        array = datatobesend  # you can send here truncated or RAW coming from your sensor in the case you use array=datatobesend that is the sensor data
        if ser.isOpen():
            print("S1C port opened")
        print("COMANDO GET DATA")
        crc16_func = crcmod.mkCrcFun(0x11021, initCrc=0x0000, xorOut=0xffff)
        command = bytearray.fromhex(array)  # your command here-
        # generates CRC based on given command
        result = hex(crc16_func(command))
        crc_1 = unhexlify(result[2] + result[3])
        crc_2 = unhexlify(result[4] + result[5])
        command.extend(crc_2+crc_1)  # appending CRC
        # array + str(crc_1) + str(crc_2)
        arraystr = str(binascii.hexlify(command))
        print(arraystr)
        logging.info('Sending TRUNCATED msg: %s' % arraystr)
        ser.write(serial.to_bytes(command))  # writing host command to smartOne
        x = ser.read(256)
        response = x.hex()
        if response != "":
            print(response)
        logging.info('TRUNCATED msg successfully sent: %s' % response)
        ser.close()
        return response
    except SerialException as e:
        print(f"ERROR: {e}")


def read_pymodbus():
    try:
        ser = serial.Serial(port=modbusport, timeout=3, baudrate=19200, bytesize=8,
                            parity='E', stopbits=1, xonxoff=False)  # Serial connect port number
        temperature = 0  # init temperature
        # command modbus depending of you modbus unit.
        command = bytearray([0x01, 0x03, 0x00, 0x2D, 0x00, 0x08, 0xD4, 0x05])
        ser.write(serial.to_bytes(command))  # writing host command to smartOne
        x = ser.read(256)
        response = x.hex()
        print("*RESPUESTA DE TEMPERATURA ACTUAL")
        print(response)
        if len(response) > 0:
            temperatura = response[:36]
        else:
            # Prinitng the response from SmartOne
            print('No Response from Modbus: ')
        ser.close()  # close port after reading
    except SerialException:
        print("Failed to open MODBUS serial port!!!")
    return temperatura


def save_to_json(esn, temperature, timestamp):
    data = {
        "esn": esn,
        "temperature": temperature,
        "timestamp": timestamp
    }
    with open("data_log.json", "a") as file:
        json.dump(data, file)
        file.write('\n')


def main():
    print("SMARTONE C Communication App")
    print("----------------------------")
    s1cport = '/dev/ttyUSB0'
    # Get ESN
    esn_response = s1c_ESN(s1cport)
    print("ESN Received:", esn_response)

    # Send a RAW data message
    example_raw_data = '012345678A'  # Example data to be sent as RAW
    #raw_response = s1c_send_data(example_raw_data, s1cport)
    #print(raw_response)


if __name__ == "__main__":
    main()
