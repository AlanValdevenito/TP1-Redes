from socket import *
import argparse

SERVER_NAME = '127.0.0.1'
SERVER_PORT = 12000

MAX_LENGTH = 10 # Envia/recibe MAX_LENGTH bits como maximo

EOF_MARKER = chr(26)

UPLOAD = 'upload'
DOWNLOAD = 'download'

ACKNOWLEDGE = 'ACK'

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

def upload(file_name, clientSocket):
    with open(file_name, 'r') as file:
        message = file.read()

        if not message.endswith(EOF_MARKER):
            message += EOF_MARKER

        len_message = len(message)
        sent_bits = 0

        while sent_bits < len_message:
            current_message = message[sent_bits:sent_bits+MAX_LENGTH]
            
            try:
                clientSocket.sendto(current_message.encode(),(SERVER_NAME, SERVER_PORT))
                acknowledge, serverAddress = clientSocket.recvfrom(MAX_LENGTH)

                if acknowledge.decode() == ACKNOWLEDGE:
                    sent_bits += MAX_LENGTH
            
            except TimeoutError:
                print(f"Timeout")
                clientSocket.sendto(message.encode(),(SERVER_NAME, SERVER_PORT))

    clientSocket.close()

def download(file_name, clientSocket):
    file = b''

    clientSocket.sendto(file_name.encode(), (SERVER_NAME, SERVER_PORT))
    while True:
        message, serverAddress = clientSocket.recvfrom(MAX_LENGTH)
        file += message
        
        clientSocket.sendto(ACKNOWLEDGE.encode(), serverAddress)

        if EOF_MARKER.encode() in message: 
            break

    with open('result_download.txt', 'w') as f:
        f.write(file.decode())

    clientSocket.close()

def main():
    args = parse_args()

    #print("Command:", args.command)
    #print("Verbose:", args.verbose)
    #print("Quiet:", args.quiet)
    #print("Host:", args.host)
    #print("Port:", args.port)
    #print("Destination File Path:", args.dst)
    #print("File Name:", args.name)

    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(2)

    clientSocket.sendto(args.command.encode(), (SERVER_NAME, SERVER_PORT))

    if args.command == UPLOAD:
        upload(args.name, clientSocket)

    if args.command == DOWNLOAD:
        download(args.name, clientSocket)
    
main()