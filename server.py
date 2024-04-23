from server_protocol import ServerProtocol
from socket_rdt import SocketRDT

MAX_LENGTH = 1024
EOF_MARKER = chr(26)

UPLOAD = 'upload'
DOWNLOAD = 'download'
ACKNOWLEDGE = 'ACK'

class Server:
    def __init__(self, ip, port):
        self.port = port
        self.server_socket = SocketRDT(ip, port, 10)
        self.connections = {}

    def start(self):
        self.server_socket.listen()
        
        while True:
            try:
                msg, address = self.server_socket.recv()
                if address not in self.connections:
                    self.connections[address] = ServerProtocol(msg.data, self.server_socket, address)
                    self.connections[address].start()

                else:
                    self.connections[address].queue.put(msg)
            except TimeoutError:
                pass
    
    def close_socket(self):
        self.server_socket.close()