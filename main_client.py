from client import Client
import argparse

SERVER_NAME = '127.0.0.1'
SERVER_PORT = 12000

UPLOAD = 'upload'
DOWNLOAD = 'download'

def parse_args():
    parser = argparse.ArgumentParser(description='Command line utility for uploading and downloading files')
    parser.add_argument('command', choices=['upload', 'download'], help='Command to execute')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
    parser.add_argument('-q', '--quiet', action='store_true', help='decrease output verbosity')
    parser.add_argument('-H', '--host', metavar='ADDR', help='server IP address')
    parser.add_argument('-p', '--port', metavar='PORT', help='server port')
    parser.add_argument('-s', '--src', metavar='DIRPATH', help='source file path')
    parser.add_argument('-d', '--dst', metavar='FILEPATH', help='destination file path')
    parser.add_argument('-n', '--name', metavar='FILENAME', help='file name')
    return parser.parse_args()

def main():
    args = parse_args()
    client = Client(SERVER_NAME, SERVER_PORT)

    if args.command == UPLOAD:
        client.upload(args.name, args.src)

    if args.command == DOWNLOAD:
        client.download(args.name, args.dst)
    
main()