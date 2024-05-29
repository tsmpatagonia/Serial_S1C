import os.path
import sys
import platform
import serial
from time import sleep
import crcmod # sudo pip install crcmod
import binascii
from binascii import unhexlify
import logging
from datetime import datetime
from collections import defaultdict
#from serial import SerialException
from random import randrange
import json
from random import randint
import os

#function to get the ESN


def s1c_send(s1cport):
    try:
        ser= serial.Serial(port=s1cport,timeout=3, baudrate = 9600,bytesize=8, parity='N', stopbits=2,xonxoff=False ) #Serial connect port number
        array = 'aa0501'
        if ser.isOpen():
            print("S1C port opened")
        print ("COMANDO GET ID")
        crc16_func = crcmod.mkCrcFun(0x11021,initCrc=0x0000,xorOut=0xffff)
        command = bytearray.fromhex(array) #your command here- Another Example: command = bytearray([0xAA,0x08,0x26, 0x10, 0x22, 0x33])
        result = hex(crc16_func(command)) # generates CRC based on given command
        crc_1 = unhexlify(result[2] + result[3])
        crc_2 = unhexlify(result[4] + result[5])
        command.extend(crc_2+crc_1) #appending CRC
        arraystr = str(binascii.hexlify(command)) #array + str(crc_1) + str(crc_2)
        ser.write(serial.to_bytes(command)) # writing host command to smartOne
        x = ser.read(256)
        response = x.hex()
        if response != "":
            print(response)
        ser.close()
        return response

    except SerialException:
        print ("ERROR")


def s1c_send_data(datatobesend, s1cport):
    try:
        ser= serial.Serial(port=s1cport,timeout=3, baudrate = 9600,bytesize=8, parity='N', stopbits=2,xonxoff=False ) #Serial connect port number
        array = 'AA0826102233' #you can send here truncated or RAW coming from your sensor in the case you use array=datatobesend that is the sensor data
        if ser.isOpen():
            print("S1C port opened")
        print ("COMANDO GET DATA")
        crc16_func = crcmod.mkCrcFun(0x11021,initCrc=0x0000,xorOut=0xffff)
        command = bytearray.fromhex(array) #your command here-
        result = hex(crc16_func(command)) # generates CRC based on given command
        crc_1 = unhexlify(result[2] + result[3])
        crc_2 = unhexlify(result[4] + result[5])
        command.extend(crc_2+crc_1) #appending CRC
        arraystr = str(binascii.hexlify(command)) #array + str(crc_1) + str(crc_2)
        print (arraystr)
        logging.info('Sending TRUNCATED msg: %s'% arraystr)
        ser.write(serial.to_bytes(command)) # writing host command to smartOne
        x = ser.read(256)
        response = x.hex()
        if response != "":
            print(response)
        logging.info('TRUNCATED msg successfully sent: %s'% response)
        ser.close()
        return response
    except SerialException:
        print ("ERROR ENVIAR DATA")
        
def read_pymodbus() :
    try:
        ser= serial.Serial(port=modbusport,timeout=3, baudrate = 19200,bytesize=8, parity='E', stopbits=1,xonxoff=False ) #Serial connect port number
        temperature=0 # init temperature
        command = bytearray([0x01 ,0x03 ,0x00, 0x2D ,0x00, 0x08, 0xD4, 0x05]) # command modbus depending of you modbus unit.
        ser.write(serial.to_bytes(command)) # writing host command to smartOne
        x = ser.read(256)
        response = x.hex()
        print("*RESPUESTA DE TEMPERATURA ACTUAL")
        print (response)
        if len(response) > 0:
            temperatura=response[:36]
        else:
            print('No Response from Modbus: ') #Prinitng the response from SmartOne
        ser.close() #close port after reading
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
    esn_response = s1c_send(s1cport)
    if esn_response:
        print("ESN Received:", esn_response)
    else:
        print("Failed to get ESN")

    # Send a RAW data message
    example_raw_data = 'AA0E27102233445566778899'  # Example data to be sent as RAW
    raw_response = s1c_send_data(example_raw_data, s1cport)
    if raw_response:
        print("RAW data sent successfully")
    else:
        print("Failed to send RAW data")

def main_loop():
    while True:
        esn = s1c_send()
        temperature = read_pymodbus()
        s1c_send_data(temperature)
        timestamp = datetime.now().isoformat()
        save_to_json(esn, temperature, timestamp)
        sleep(2700)  # Sleep for 45 minutes

if __name__ == "__main__":
    main()
