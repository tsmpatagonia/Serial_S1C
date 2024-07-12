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

########- ----------------------- REMOVE from test in RASPBERRY
#import RPi.GPIO as GPIO
########- ----------------------- REMOVE from test in RASPBERRY

import time
import datetime

# Set up the GPIO mode
#GPIO.setmode(GPIO.BCM)

# Set up the GPIO pin for reading the DO output
#DO_PIN = 7  # Replace with the actual GPIO pin number
#GPIO.setup(DO_PIN, GPIO.IN)
#NO ANDA GASREAD!!!!
#def gasRead():
#    try:
#        while True:
#            # Read the state of the DO pin
#            gas_present = GPIO.input(DO_PIN)

            # Determine if gas is present or not
#            if gas_present == GPIO.LOW:
#                gas_state = "Gas Present"
#                #log_event(gas_state)
#            else:
#                gas_state = "No Gas"

            # Print the gas state
#            print(f"Gas State: {gas_state}")
            # log_event(gas_state)

#            time.sleep(0.5)  # Wait for a short period before reading again

#    except KeyboardInterrupt:
#        print("Gas detection stopped by user")

#    finally:
        # Clean up GPIO settings
#        GPIO.cleanup()


def s1c_ESN(s1cport):
    try:
        # Configuración de la conexión serial
        ser = serial.Serial(
            port=s1cport,
            timeout=5,  # Incrementar tiempo de espera
            baudrate=9600,
            bytesize=8,
            parity='N',
            stopbits=2,
            xonxoff=False
        )

        # Comando para obtener el ESN
        array = 'aa0501'
        # time.sleep(3)

        if ser.isOpen():
            print("S1C port opened")

        print("COMANDO GET ID")
        # time.sleep(5)

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
        #time.sleep(5)

        # Leer la respuesta
        x = ser.read(256)
        response = x.hex()

        if response:
            print("ESN Received:", response)

            # Decodificar la respuesta
            if response.startswith("aa"):
                length = int(response[2:4], 16)
                command_id = response[4:6]
                esn_hex = response[6:-4]  # Extraer ESN en hexadecimal
                crc_received = response[-4:]

                # Convertir ESN de hexadecimal a decimal
                esn_decimal = int(esn_hex, 16)

                # Formatear ESN al formato deseado
                esn_formatted = f"0-{esn_decimal}"

                print(f"Length: {length}")
                print(f"Command ID: {command_id}")
                print(f"ESN (Hex): {esn_hex}")
                print(f"ESN (Decimal): {esn_decimal}")
                print(f"ESN (Formatted): {esn_formatted}")
                print(f"CRC Received: {crc_received}")

        else:
            print("No response received")

        # Cerrar la conexión serial
        ser.close()

        return response

    except SerialException as e:
        print(f"ERROR: {e}")

def s1c_send_data(user_data, s1cport, msg_type):
    try:
        ser = serial.Serial(port=s1cport, timeout=3, baudrate=9600, bytesize=8,
                            parity='N', stopbits=2, xonxoff=False)  # Serial connect port number

        # Convertir datos de usuario a hexadecimal
        datatobesend = user_data.encode('utf-8').hex()

        # Seleccionar el tipo de comando
        if msg_type == "truncated":
            cmd = "26"
            max_data_len = 47  # Máximo de 47 bytes de datos de usuario para mensajes truncados
        elif msg_type == "raw":
            cmd = "27"
            max_data_len = 53  # Máximo de 53 bytes de datos de usuario para mensajes RAW
        else:
            print("Tipo de mensaje no válido")
            return

        # Verificar que los datos de usuario no excedan el límite permitido
        data_len = len(datatobesend) // 2
        if data_len > max_data_len:
            print(
                f"Los datos de usuario no pueden exceder {max_data_len} bytes")
            return

        # Longitud del comando en hexadecimal
        length = format(5 + data_len, '02x')

        # Construir el comando completo
        array = f'aa{length}{cmd}{datatobesend}'

        if ser.isOpen():
            print("S1C port opened")

        print(f"COMANDO GET {msg_type.upper()} DATA")
        crc16_func = crcmod.mkCrcFun(0x11021, initCrc=0x0000, xorOut=0xffff)
        command = bytearray.fromhex(array)
        

        # Generar CRC basado en el comando dado
        result = hex(crc16_func(command))
        crc_1 = unhexlify(result[2:4])
        crc_2 = unhexlify(result[4:6])
        #crc_1 = unhexlify(result[2:4])
        #crc_2 = unhexlify(result[4:6])
        command.extend(crc_2 + crc_1)  # appending CRC

        #ser.write(serial.to_bytes(command))
        ser.write(command)  # writing host command to smartOne
        x = ser.read(256)
        response = x.hex()

        if response:
            print(command)
            print(array)
            print(response)

        ser.close()
        return response
    except SerialException:
        print("ERROR ENVIAR DATA")

def s1c_send_data_MOD(user_data, s1cport, msg_type):
    try:
        ser = serial.Serial(port=s1cport, timeout=3, baudrate=9600, bytesize=8,
                            parity='N', stopbits=2, xonxoff=False)  # Serial connect port number

        # Convertir datos de usuario a hexadecimal
        datatobesend = user_data.encode('utf-8').hex()
        
        # Seleccionar el tipo de comando
        if msg_type == "truncated":
            cmd = "26"
            max_data_len = 47  # Máximo de 47 bytes de datos de usuario para mensajes truncados
        elif msg_type == "raw":
            cmd = "27"
            max_data_len = 53  # Máximo de 53 bytes de datos de usuario para mensajes RAW
        else:
            print("Tipo de mensaje no válido")
            return

        # Verificar que los datos de usuario no excedan el límite permitido
        data_len = len(datatobesend) // 2
        if data_len > max_data_len:
            print(f"Los datos de usuario no pueden exceder {max_data_len} bytes")
            return

        # Longitud del comando en hexadecimal
        length = format(5 + data_len, '02x')

        # Construir el comando completo
        array = f'aa{length}{cmd}{datatobesend}'

        if ser.isOpen():
            print("S1C port opened")

        print(f"COMANDO GET {msg_type.upper()} DATA")
        crc16_func = crcmod.mkCrcFun(0x11021, initCrc=0x0000, xorOut=0xffff)
        command = bytearray.fromhex(array)

        # Generar CRC basado en el comando dado
        result = hex(crc16_func(command))[2:]  # Remove '0x' from the beginning
        result = result.zfill(4)  # Ensure it's 4 characters long
        crc_1 = unhexlify(result[2:])
        crc_2 = unhexlify(result[:2])
        command.extend(crc_2 + crc_1)  # Append CRC

        # Enviar el comando al dispositivo
        #ser.write(serial.to_bytes(command))
        ser.write(command)  # writing host command to smartOne
        x = ser.read(256)
        response = x.hex()

        if response:
            print(f"Comando enviado: {binascii.hexlify(command).decode()}")
            print(f"Array original: {array}")
            print(f"Respuesta recibida: {response}")

        ser.close()
        return response
    except serial.SerialException as e:
        print(f"ERROR ENVIAR DATA: {e}")





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
        print("\nSMARTONE C Super! Communication App")
        print("----------------------------")
        print("1. Averiguar el ESN")
        print("2. Mandar un mensaje")
        print("3. Salir")
        choice = input("Elige una opción: ")

        if choice == '1':
            esn_response = s1c_ESN(s1cport)
            print("ESN Received:", esn_response)

        elif choice == '2':
            msg_type = input(
                "Introduce el tipo de mensaje (truncated/raw): ").strip().lower()
            if msg_type not in ["truncated", "raw"]:
                print("Tipo de mensaje no válido. Inténtalo de nuevo.")
                continue
            user_data = input(
                "Introduce los datos de usuario en formato alfanumérico: ")
            esn_response = s1c_ESN(s1cport)
            # print("ESN Received:", esn_response)
            response = s1c_send_data(user_data, s1cport, msg_type)
            print(f"Respuesta {msg_type.upper()}: {response}")

        elif choice == '3':
            print("Saliendo...")
            break

        else:
            print("Opción no válida. Inténtalo de nuevo.")


if __name__ == "__main__":
    main()
