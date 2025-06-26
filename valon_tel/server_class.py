import time
from valon_tel.valon_control import ValonSynth 
from pathlib import Path
import socket
import signal
import logging
import threading
import signal
import os
import json

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
        self.setup_signal_handler()

        try:
            self.logger.info(f"connecting to Valon on {self.valon_port}")
            # i dont think im creatinf this object correctly yet. well becayse the cli has a port alr. specifiied but lowk it may be ok
            self.valon = ValonSynthTelemetry(port=self.valon_port)

            threads =[]

            #each socket will be seperate 
            self.telem_server_socket = self.setup_socket(socket_path=self.telem_socket_path,backlog=10,description="Telemetry")
            self.cli_server_socket = self.setup_socket(socket_path=self.cli_socket_path,backlog=2,description="CLI")

            #thread to poll the valon in the background
            threading.Thread(target=self.telem_loop, daemon=True).start()
            threading.Thread(target=self.telem_server_loop, daemon=True).start()

            #main thread is the cli
            self.cli_server_loop()

        except Exception as e:
            self.logger.error(f"Error starting server: {e}")
            self.stop()
            raise

    def stop(self):
        self.running = False
        self.logger.info(f"ending socket servers")

        if self.telem_server_socket:
            self.telem_server_socket.close()
        if self.cli_server_socket:
            self.cli_server_socket.close()

        #remove from disk bc otherwise gonna have trouble on next rreboot
        for path in [self.telem_socket_path, self.cli_socket_path]:
            if os.path.exists(path):
                os.unlink(path)

    def setup_socket(self, socket_path, backlog=5, description=""):
        if os.path.exists(socket_path):
            os.unlink(socket_path)

        #get directory conatining the socket file
        socket_dir = Path(socket_path).parent
        socket_dir.mkdir(parents=True, exist_ok=True)

        try:
            server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) #unix domain socket
            server_socket.bind(socket_path)
            server_socket.listen(backlog)
    
            #read/write for everyone
            os.chmod(socket_path, 0o666)
            self.logger.info(f"socket server listening on {socket_path}")
            return server_socket

        except (socket.error, OSError) as e:
            self.logger.error(f"socket error for {description}: {e}")
            raise

    def telem_loop(self):
        """valon polling"""
        self.logger.info(f"starting polling valon")

        while self.running:
            try:
                telem = self.valon.read_telem()
                with self.telem_lock:
                    self.last_telem = telem

                self.logger.info(f"updated telemetry: {telem}")
                
            except Exception as e:
                self.logger.error(f"error polling telemetry: {e}")

                # save latest
                with self.telem_lock:
                    self.last_telem = {
                        "timestamp": time.time(),
                        "error": str(e),
                        "device_port": self.valon_port
                    }

            time.sleep(self.poll_interval)

    def telem_server_loop(self):
        """handling telem request from bens service"""
        self.logger.info(f"starting thread to distribute valon telemetry")

        while self.running:
            try:
                self.telem_server_socket.settimeout(1.0)
                client_socket, addr = self.telem_server_socket.accept()

                self.handle_service_client(client_socket)

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    self.logger.error(f"error in telemetry server loop: {e}")


    def handle_service_client(self, client_socket):
        try:
            with client_socket:
                with self.telem_lock:
                    telem_data = self.last_telem.copy()

                    response = json.dumps(telem_data) + "\n"
                    client_socket.sendall(response.encode('utf-8'))

        except Exception as e:
            self.logger.error(f"error handling telemetry client: {e}")

    def cli_server_loop(self):
        """handle cli socket client"""
        self.logger.info(f"starting thread to distribute valon telemetry")

        while self.running:
            try:
                self.cli_server_socket.settimeout(1.0)
                client_socket, addr = self.cli_server_socket.accept()

                self.handle_cli_client(client_socket)

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    self.logger.error(f"error in cli server loop: {e}")

    def handle_cli_client(self, client_socket):
        try:
            with client_socket:
                data = client_socket.recv(1024).decode('utf-8').strip()

                if not data:
                    return
                
                self.logger.info(f"Received CLI command: {data}")
                response = self.execute_cli_command(data)
                client_socket.sendall((response + "\n").encode('utf-8'))

        except Exception as e:
            self.logger.error(f"error handling cli client: {e}")

    def execute_cli_command(self, cmd):
        if cmd.startswith("F"):
            return self.valon.set_freq(cmd)
        elif cmd.startswith("PWR"):
            return self.valon.set_power(cmd)
