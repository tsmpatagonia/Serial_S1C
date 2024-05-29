import os.path
import sys
import platform
import serial
from time import sleep
import crcmod  # sudo pip install crcmod
import binascii
from binascii import unhexlify
import logging
from datetime import datetime
import time
from collections import defaultdict
from serial import SerialException
from random import randrange
from random import randint
import os

# function to get the ESN


def s1c_send():


try:
ser = serial.Serial(port=s1cport, timeout=3, baudrate=9600, bytesize=8,
                    parity='N', stopbits=2, xonxoff=False)  # Serial connect port number
array = 'aa0501'
if ser.isOpen():
print("S1C port opened")
print("COMANDO GET ID")
crc16_func = crcmod.mkCrcFun(0x11021, initCrc=0x0000, xorOut=0xffff)
# your command here- Another Example: command = bytearray([0xAA,0x08,0x26, 0x10, 0x22, 0x33])
command = bytearray.fromhex(array)
result = hex(crc16_func(command))  # generates CRC based on given command
crc_1 = unhexlify(result[2] + result[3])
crc_2 = unhexlify(result[4] + result[5])
command.extend(crc_2+crc_1)  # appending CRC
arraystr = str(binascii.hexlify(command))  # array + str(crc_1) + str(crc_2)
ser.write(serial.to_bytes(command))  # writing host command to smartOne
