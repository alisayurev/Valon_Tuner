#!/usr/bin/env python3

"""

Valon 5015/5019 RF Synthesizer CLI Tool

Command-line interface for Valon RF synthesizer

"""

import sys
import argparse
import serial  
import serial.tools.list_ports as list_ports
import os
import time

#consider dtr -> i think its just a hard reset for the tuner
#can also change baudrate if somrthing goes wrong
#write may always require a carriage return i am unsure

#remove this once the udev rules work :3
def list_available_ports():
 
    ports = list_ports.comports()
    for port in ports:
        print(port)

class ValonSynth():

    def __init__(self, port = "/dev/ttyUSB0", baudrate = 9600):

        self.port = port
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=1)
        if not self.ser.is_open:
            self.ser.open()
            print(f"connected to Valon on {port} at {baudrate} baud.")

        self.ser.reset_input_buffer()

    def send(self, command):

        self.ser.write((command + "\r").encode())
        time.sleep(0.1)
        response = b""

        while self.ser.in_waiting:
            response += self.ser.read(self.ser.in_waiting)

        return response.decode(errors='ignore')

    #ask if mhz or ghz -> doesnt relaly matter just user need sto know
    def set_freq(self, freq_ghz):

        freq_mhz = int(freq_ghz * 1000)
        cmd = f"F{freq_mhz}MHz"
        print(f"Sending frequency command: {cmd}")
        return self.send(cmd)
    
    def set_power(self, mod_dB):
        cmd = f"PWR {mod_dB}"
        print(f"Sending power command: {cmd}")
        return self.send(cmd)

    def close(self):
        self.ser.reset_input_buffer()
        self.ser.close()

if __name__ == "__main__":

    list_available_ports()
    parser = argparse.ArgumentParser()
    parser.add_argument("--freq", "-f", type=float, required=True, help= "freq in gigahertz")
    parser.add_argument("--power", "-p", type=int, required=False, help="i dont know the power reference yet")
    args = parser.parse_args()

    valon = ValonSynth()
    result_freq = valon.set_freq(args.freq)
    print(result_freq)
    if args.power:
        result_power = valon.set_power(args.power)
        print(result_power)
    valon.close()


 
# if i want the synthesizer to start up at a certain config -> send the SAV command. (saves settings to flash)
# ask about default settings 

 