#!/usr/bin/env python3

"""
Valon 5015/5019 RF Synthesizer Telemetry Server
Polls Valon synthesizer for telemetry data and serves it via Unix socket.
Designed to run as a systemd service on Nvidia Jetson Linux systems.
Alisa Yurevich 06/2025
"""

import time
from valon_control import ValonSynth 
from pathlib import Path
import socket
import signal
import argparse
import logging
import threading
import signal
import os

#unix socket server will be opened on the jetson through a systemd service
#if i include, valon_control needs to be in my python path

#will there be a problem reading? like someone will run the cli, which basically just sends comm
# but it also reads. idk about the timing for that, if this script/service will interfere?

# basically instead of dealing with this issue in a weird roundabout way,
# the telem service will handle the CLI and the requests from the other service

class ValonSynthTelemetry(ValonSynth):
    """
    Extension of Valon CLI that will poll the tuner for info + return telemetry
    """

    # TO DO: test calling readfreq and read power. need to know the querying works
    def read_freq(self):
        try:
            response = self.send("F?")
            return response.strip()
        except Exception as e:
            logging.error(f"error getting frequency: {e}")
            return None
    
    def read_power(self):
        try:
            response = self.send("PWR?")
            return response.strip()
        except Exception as e:
            logging.error(f"error getting power: {e}")
            return None
        
    def read_telem(self):
        return {
            "timestamp": time.time(), 
            "frequency": self.read_freq(),
            "power": self.read_power(),
        }

class Valon_Sock:
    """
    Server that polls Valon for telemetry and serves data via Unix socket
    """
    #ask ben about the poll interval
    def __init__(self, telem_socket_path="/tmp/valon_telem.sock", cli_socket_path = "/tmp/valon_cli.sock", poll_interval=0.1,valon_port="/dev/valon5015"):
        self.telem_socket_path = telem_socket_path          
        self.cli_socket_path = cli_socket_path
        self.poll_interval = poll_interval
        self.valon_port = valon_port
        self.running = False                    #status of the service
        self.valon = None                       #will hold a valon obj
        self.telem_server_socket = None  
        self.cli_server_socket = None             #will hold the socket once its opened + initialized
        self.last_telem = {}                    #last telem dictionary
        self.telem_lock = threading.Lock()

        #since we are threading lets set up a log :3
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        self.logger = logging.getLogger(__name__)

    def setup_signal_handler(self):
        #signal module will basically call the handler if it recieves these
        signal.signal(signal.SIGTERM, self._sig_handler)
        signal.signal(signal.SIGINT, self._sig_handler)

    def _sig_handler(self,signum,frame):
        self.logger.info(f"recieved {signum}")
        self.stop()
        pass

    def start(self):
        """start telem server thread"""

        self.running = True

        try:
            self.logger.info(f"connecting to Valon on {self.valon_port}")
            # i dont think im creatinf this object correctly yet. well becayse the cli has a port alr. specifiied but lowk it may be ok
            self.valon = ValonSynthTelemetry(port=self.valon_port)

            #each socket will be seperate 
            self.telem_server_socket = self.setup_socket(self.telem_socket_path,backlog=10,description="Telemetry")
            self.cli_server_socket = self.setup_socket(self.cli_socket_path,backlog=2,description="CLI")

            #thread to poll the valon in the background
            threading.Thread(target=self.telem_loop, daemon=True).start() # this will call telem_loop, and this thread will run in thr background
            threading.Thread(target=self.telem_server_loop, daemon=True).start()

            #main thread is the cli
            self.cli_server_loop()

        except Exception as e:
            self.logger.error(f"Error starting server: {e}")
            self.stop()
            raise

    def stop(self):
        self.running = False
        # need to remove both socket files from disk

    def setup_socket(self, socket_path, backlog=5, description=""):
        if os.path.exists(socket_path):
            os.unlink(socket_path)

        #get directory conatining the socket file
        socket_dir = Path(socket_path).parent
        socket_dir.mkdir(parents=True, exist_ok=True)

        try:
            server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) #unix domain socket
        except (socket.error, BrokenPipeError) as e:
            self.logger.info(f"socket error: {e}")
     
        server_socket.bind(socket_path)
        server_socket.listen(backlog)
    
        #read/write for everyone
        os.chmod(socket_path, 0o666)
        self.logger.info(f"socket server listening on {self.socket_path}")

        return server_socket

    def telem_loop(self):
        """valon polling"""
        self.logger.info(f"starting polling valon")

        while self.running:
            try:
                telem = self.valon.read_telem()
                with self.telem_lock:
                    self.latest_telemetry = telem

                self.logger.info(f"updated telemetry: {telem}")
                
            except Exception as e:
                self.logger.error(f"error polling telemetry: {e}")

                # save latest
                with self.telem_lock:
                    self.latest_telemetry = {
                        "timestamp": time.time(),
                        "error": str(e),
                        "device_port": self.valon_port
                    }

            time.sleep(self.poll_interval)

    def telem_server_loop(self):
        pass

    def cli_server_loop(self):
        pass





