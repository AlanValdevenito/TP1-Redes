from socket import *
import argparse

SERVER_PORT = 12000

EOF_MARKER = chr(26)

MAX_LENGTH = 10 # Envia/recibe MAX_LENGTH bits como maximo

UPLOAD = 'upload'
DOWNLOAD = 'download'

ACKNOWLEDGE = 'ACK'

def parse_args():
    parser = argparse.ArgumentParser(description='<command description>')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
    parser.add_argument('-q', '--quiet', action='store_true', help='decrease output verbosity')
    parser.add_argument('-H', '--host', metavar='ADDR', help='service IP address')
    parser.add_argument('-p', '--port', metavar='PORT', help='service port')
    parser.add_argument('-s', '--storage', metavar='DIRPATH', help='storage dir path')
    return parser.parse_args()

def upload(serverSocket):
  file = b''

  while True:
    message, clientAddress = serverSocket.recvfrom(MAX_LENGTH)
    file += message
    
    serverSocket.sendto(ACKNOWLEDGE.encode(), clientAddress)
    
    if EOF_MARKER.encode() in message: 
      break

  with open('result_upload.txt', 'w') as f:
    f.write(file.decode())

  serverSocket.close()

def download(serverSocket):
  
  file_name, clientAddress = serverSocket.recvfrom(MAX_LENGTH)
  with open(file_name, 'r') as file:
        message = file.read()

        if not message.endswith(EOF_MARKER):
            message += EOF_MARKER

        len_message = len(message)
        sent_bits = 0

        while sent_bits < len_message:

            current_message = message[sent_bits:sent_bits+MAX_LENGTH]
            
            try:
                serverSocket.sendto(current_message.encode(), clientAddress)
                acknowledge, serverAddress = serverSocket.recvfrom(MAX_LENGTH)

                if acknowledge.decode() == ACKNOWLEDGE:
                    sent_bits += MAX_LENGTH
            
            except TimeoutError:
                print(f"Timeout")
                serverSocket.sendto(message.encode(),clientAddress)

  serverSocket.close()

def main():
  args = parse_args()

  serverSocket = socket(AF_INET, SOCK_DGRAM)
  serverSocket.bind(('', SERVER_PORT))
  
  type, clientAddress = serverSocket.recvfrom(MAX_LENGTH)

  if type.decode() == UPLOAD:
    upload(serverSocket)
  
  if type.decode() == DOWNLOAD:
    download(serverSocket)

main()