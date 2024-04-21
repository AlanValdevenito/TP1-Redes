from server_protocol import ServerProtocol
from session import Session

MAX_LENGTH = 10
EOF_MARKER = chr(26)

UPLOAD = 'upload'
DOWNLOAD = 'download'
ACKNOWLEDGE = 'ACK'

class Server:
    def __init__(self, ip, port, protocol):
        self.port = port
        self.server_socket = ServerProtocol(ip, port, protocol, 10)
        self.connections = {}

    def start(self):
        self.server_socket.listen()
        
        while True:
            msg, address = self.recv()

            if address not in self.connections:
                self.connections[address] = Session(msg.decode(), self.server_socket, address)
                self.connections[address].start()

            else:
                self.connections[address].queue.put(msg)

    def send(self, message, address):
        self.server_socket.send(message, address)

    def recv(self):
        return self.server_socket.recv()
    
    def close_socket(self):
        self.server_socket.close()