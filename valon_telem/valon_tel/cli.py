import argparse
from valon_tel.client_socket import send_command_socket

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--freq", "-f", type=float, required=True, help= "freq in megahertz")
    parser.add_argument("--power", "-p", type=int, required=False, help="power in dB")
    args = parser.parse_args()

    response = send_command_socket(f"F{args.freq}MHz")
    print(response)
    if args.power is not None:
        response = send_command_socket(f"PWR {args.power}")
        print(response)