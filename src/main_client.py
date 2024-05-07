import argparse
from client import Client
from utils import check_client_args
from config import UPLOAD, DOWNLOAD, IP, SERVER_PORT, PORT


def parse_args():
    parser = argparse.ArgumentParser(
        description='Command line utility for uploading and downloading files')
    parser.add_argument(
        'command', choices=['upload', 'download'], help='Command to execute')
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='increase output verbosity')
    parser.add_argument(
        '-q', '--quiet', action='store_true', help='decrease output verbosity')
    parser.add_argument(
        '-H', '--host', metavar='ADDR', default=IP, help='server IP address')
    parser.add_argument(
        '-p', '--port', metavar='PORT', default=SERVER_PORT,
        help='server port')
    parser.add_argument(
        '-s', '--src', metavar='FILEPATH', help='source file path')
    parser.add_argument(
        '-d', '--dst', metavar='FILEPATH', help='destination file path')
    parser.add_argument('-n', '--name', metavar='FILENAME', help='file name')
    parser.add_argument(
        '-P', '--protocol', metavar='PROTOCOL', help='protocol number')
    return parser.parse_args()


def main():
    args = parse_args()
    if not check_client_args(args):
        return

    client = Client(args.host, PORT, args)
    server_address = (args.host, args.port)

    if args.command == UPLOAD:
        client.upload(args.src, args.name, server_address)

    if args.command == DOWNLOAD:
        client.download(args.dst, args.name, server_address)


main()
