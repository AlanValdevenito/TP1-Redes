from server import Server
import argparse

SERVER_PORT = 12000

def parse_args():
    parser = argparse.ArgumentParser(description='<command description>')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
    parser.add_argument('-q', '--quiet', action='store_true', help='decrease output verbosity')
    parser.add_argument('-H', '--host', type=str, default='', metavar='ADDR', help='service IP address')
    parser.add_argument('-p', '--port', type=int, default=SERVER_PORT, metavar='PORT', help='service port')
    parser.add_argument('-s', '--storage', metavar='DIRPATH', help='storage dir path')
    return parser.parse_args()

def main():
  args = parse_args()
  server = Server(args.host, args.port)
  server.start()

main()