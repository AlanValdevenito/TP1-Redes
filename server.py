from socket_UDP import Socket
from session import Session
import queue

MAX_LENGTH = 10
EOF_MARKER = chr(26)

UPLOAD = 'upload'
DOWNLOAD = 'download'
ACKNOWLEDGE = 'ACK'

class Server:
    def __init__(self, ip, port, protocol):
        self.port = port
        self.server_socket = Socket(ip, port, protocol, 10)
        self.send_queue = queue.Queue()
        self.connections = {}

    def start(self):
        self.server_socket.listen()

        while True:
            type, address = self.recv()

            print(f"Se conecto un cliente {address}")
            if address not in self.connections:
                self.connections[address] = Session(type, self.send_queue, address)
                self.connections[address].start()

    def process_request(self, request_type):
        if request_type == UPLOAD:
            self.upload()
        elif request_type == DOWNLOAD:
            self.download()

    def send(self, message, address):
        self.server_socket.send(message, address)

    def recv(self):
        return self.server_socket.recv()
    
    def close_socket(self):
        self.server_socket.close()

    def upload(self):
        file_name, _ = self.recv()
        file, _ = self.recv()

        with open(file_name, 'w', encoding='latin-1') as f:
          f.write(file)

        self.close_socket()
    
    def download(self):
      file_name, clientAddress = self.recv()
      with open(file_name, 'r', encoding='latin-1') as file:
            message = file.read()
            self.send(message, clientAddress)

      self.close_socket()