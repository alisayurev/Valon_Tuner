#!/usr/bin/env python3

"""

Valon 5015/5019 RF Synthesizer CLI Tool

Command-line interface for Valon RF synthesizer on Nvidia Jetson Linux systems.
This tool configures the synthesizer via USB serial connection.

Alisa Yurevich 06/2025 

"""
import argparse
import serial  
import time
import socket       # instead of this cli doing the direct connection, the connection will be done through a socket
                    # the service will connect to the port
                    # this also means that this script will probably need to be added on the machines python path.
                    # 
import json 

CLI_SOCKET_PATH = "/tmp/valon_cli.sock"

def send_command_socket(cmd):
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect(CLI_SOCKET_PATH)
            sock.sendall(cmd.encode('utf-8'))
            response = sock.recv(1024)
            return response.decode('utf-8')
    except Exception as e:
        return f"socket error: {e}"

class ValonSynth():
    """
    Class for communicating with a Valon 5015 RF Synthesizer
    over a serial connection.
    """

    def __init__(self, port = "/dev/valon5015", baudrate = 9600): # baud rate can be made higher accordingly
        """
        Initialize the serial connection to the Valon device.
        Assumes a persistent udev symlink has been created (e.g., /dev/valon5015).
        """
        self.port = port
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=1)

        if not self.ser.is_open: 
            self.ser.open()

        # one way to clear -> can also turn dtr on and off
        self.ser.reset_input_buffer() 

    def send(self, command):
        """
        Send a command string to the Valon over serial.
        Appends carriage return. Returns any response.
        """
        self.ser.write((command + "\r").encode())
        time.sleep(0.1)
        response = b""

        while self.ser.in_waiting:
            response += self.ser.read(self.ser.in_waiting)

        return response.decode(errors='ignore')

    def set_freq(self, freq_mhz):
        """
        Set the output frequency of the synthesizer.
        """
        cmd = f"F{freq_mhz}MHz"
        print(f"Sending frequency command: {cmd}")
        return self.send(cmd)
    
    def set_power(self, mod_dB):
        """
        Set output power level. Valid Range -50 - 20. Can be brought lower 
        configuring extra settings in the Valon.
        """
        cmd = f"PWR {mod_dB}"
        print(f"Sending power command: {cmd}")
        return self.send(cmd)

    def close(self):
        """
        Close serial connection.
        """
        self.ser.reset_input_buffer()
        self.ser.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--freq", "-f", type=float, required=True, help= "freq in megahertz")
    parser.add_argument("--power", "-p", type=int, required=False, help="power in dB")
    args = parser.parse_args()

    response = send_command_socket(f"F{args.freq}MHz")
    print(response)
    if args.power is not None:
        response = send_command_socket(f"PWR {args.power}")
        print(response)