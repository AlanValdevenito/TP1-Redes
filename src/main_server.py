from server import *
import argparse

IP = "127.0.0.1"
PORT = 12000
DEFAULT_PATH = 'server_storage/'


def parse_args():
    parser = argparse.ArgumentParser(description='<command description>')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
    parser.add_argument('-q', '--quiet', action='store_true', help='decrease output verbosity')
    parser.add_argument('-H', '--host', metavar='ADDR', help='service IP address')
    parser.add_argument('-p', '--port', metavar='PORT', help='service port')
    parser.add_argument('-s', '--storage', metavar='DIRPATH', default=DEFAULT_PATH, help='storage dir path')
    parser.add_argument('-P', '--protocol', metavar='PROTOCOL', help='protocol number')
    return parser.parse_args()


def main():
    args = parse_args()

    server = Server(IP, PORT, args.protocol, args.storage)
    server.start()


main()
