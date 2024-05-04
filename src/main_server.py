from server import *
from config import IP, SERVER_PORT, DEFAULT_PATH
from utils import check_server_args
import argparse


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
    if not check_server_args(args):
        return

    server = Server(IP, SERVER_PORT, args)
    server.start()


main()
