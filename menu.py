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
        print("COMANDO put DATA")
        crc16_func = crcmod.mkCrcFun(0x11021, initCrc=0x0000, xorOut=0xffff)
        command = bytearray.fromhex(array)  # your command here-
        # generates CRC based on given command
        result = hex(crc16_func(command))
        crc_1 = unhexlify(result[2:4])
        crc_2 = unhexlify(result[4:6])
        command.extend(crc_2 + crc_1)  # appending CRC
        arraystr = str(binascii.hexlify(command))
        print(arraystr)
        print('Sending TRUNCATED msg: %s' % arraystr)
        ser.write(serial.to_bytes(command))  # writing host command to smartOne
        x = ser.read(256)
        response = x.hex()
        if response != "":
            print(response)
        print('TRUNCATED msg successfully sent: %s' % response)
        ser.close()
        return response
    except SerialException:
        print("ERROR ENVIAR DATA")


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
    s1cport = '/dev/ttyUSB0'
    while True:
        print("\nSMARTONE C Communication App")
        print("----------------------------")
        print("1. Averiguar el ESN")
        print("2. Mandar un mensaje RAW")
        print("3. Salir")
        choice = input("Elige una opción: ")

        if choice == '1':
            esn_response = s1c_ESN(s1cport)
            print("ESN Received:", esn_response)

        elif choice == '2':
            raw_data = input(
                "Introduce el texto a mandar (en formato hexadecimal): ")
            raw_response = s1c_send_data(raw_data, s1cport)
            print("Respuesta RAW:", raw_response)

        elif choice == '3':
            print("Saliendo...")
            break

        else:
            print("Opción no válida. Inténtalo de nuevo.")


if __name__ == "__main__":
    main()
