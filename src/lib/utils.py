import argparse
from .config import UPLOAD, DOWNLOAD, IP, SERVER_PORT, DEFAULT_PATH


def check_verbose_quiet(args):
    if args.verbose and args.quiet:
        print('Error: Cannot use both verbose and quiet flags')
        return False
    return True


def check_client_args(args):
    if args.command == UPLOAD and not args.src:
        print('Error: Source file path is required for upload command')
        return False
    if args.command == DOWNLOAD and not args.dst:
        print('Error: Destination file path is required for download command')
        return False
    if not args.name:
        print('Error: File name is required')
        return False
    return check_verbose_quiet(args)


def check_server_args(args):
    return check_verbose_quiet(args)


def parse_server_args():
    d = 'Command line server utility for uploading and downloading files'
    parser = argparse.ArgumentParser(description=d)

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-v', '--verbose', action='store_true',
        help='increase output verbosity')
    group.add_argument(
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
