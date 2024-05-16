import serial
import crcmod
import binascii
from serial import SerialException
from datetime import datetime
import json
from time import sleep

# Assuming s1cport and modbusport are defined and set properly for your serial connections

def get_esn():
    try:
        with serial.Serial(port=s1cport, timeout=3, baudrate=9600, bytesize=8, parity='N', stopbits=2, xonxoff=False) as ser:
            print("S1C port opened")
            print("COMMAND GET ID")
            command = bytearray.fromhex('aa0501')
            crc16_func = crcmod.mkCrcFun(0x11021, initCrc=0, xorOut=0xFFFF)
            command += crc16_func(command).to_bytes(2, byteorder='big')
            ser.write(command)
            response = ser.read(256).hex()
            if response:
                print(response)
            return response
    except SerialException:
        print("ERROR")

def read_temperature():
    try:
        with serial.Serial(port=modbusport, timeout=3, baudrate=19200, bytesize=8, parity='E', stopbits=1, xonxoff=False) as ser:
            print("Modbus port opened")
            command = bytearray([0x01, 0x03, 0x00, 0x2D, 0x00, 0x08, 0xD4, 0x05])
            ser.write(command)
            response = ser.read(256).hex()
            if response:
                print("*CURRENT TEMPERATURE RESPONSE")
                print(response)
                return response[:36]
            else:
                print('No Response from Modbus')
    except SerialException:
        print("Failed to open MODBUS serial port!!!")
    return ''

def send_data(data):
    try:
        with serial.Serial(port=s1cport, timeout=3, baudrate=9600, bytesize=8, parity='N', stopbits=2, xonxoff=False) as ser:
            print("S1C port opened")
            print("COMMAND SEND DATA")
            crc16_func = crcmod.mkCrcFun(0x11021, initCrc=0, xorOut=0xFFFF)
            command = bytearray.fromhex(data)
            command += crc16_func(command).to_bytes(2, byteorder='big')
            ser.write(command)
            response = ser.read(256).hex()
            if response:
                print(response)
            return response
    except SerialException:
        print("ERROR SEND DATA")

def save_to_json(esn, temperature, timestamp):
    data = {
        "esn": esn,
        "temperature": temperature,
        "timestamp": timestamp
    }
    with open("data_log.json", "a") as file:
        json.dump(data, file)
        file.write('\n')

def main_loop():
    while True:
        esn = get_esn()
        temperature = read_temperature()
        send_data(temperature)
        timestamp = datetime.now().isoformat()
        save_to_json(esn, temperature, timestamp)
        sleep(2700)  # Sleep for 45 minutes

if __name__ == "__main__":
    main_loop()
