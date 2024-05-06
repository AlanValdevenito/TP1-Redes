import argparse
from server import Server
from config import IP, SERVER_PORT, DEFAULT_PATH
from utils import check_server_args


def parse_args():
    parser = argparse.ArgumentParser(description='<command description>')
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='increase output verbosity')
    parser.add_argument(
        '-q', '--quiet', action='store_true', help='decrease output verbosity')
    parser.add_argument(
        '-H', '--host', metavar='ADDR', default=IP, help='service IP address')
    parser.add_argument(
        '-p', '--port', metavar='PORT', default=SERVER_PORT,
        help='service port')
    parser.add_argument(
        '-s', '--storage', metavar='DIRPATH', default=DEFAULT_PATH,
        help='storage dir path')
    parser.add_argument(
        '-P', '--protocol', metavar='PROTOCOL', help='protocol number')
    return parser.parse_args()


def main():
    print("Server started")
    args = parse_args()

    if not check_server_args(args):
        return

    print(args.host)
    server = Server(args.host, args.port, args)
    server.start()


main()
