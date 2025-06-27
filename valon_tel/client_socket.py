import socket      
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