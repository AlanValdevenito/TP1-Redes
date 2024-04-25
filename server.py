from message import MessageType
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
                print(f"Llega algo del cliente {address}")
                #print(f"Server.start: Llega el mensaje '{msg.data}' con numero de secuencia '{msg.sequence_number}'\n")
                if address not in self.connections:
                    #print(f"Server.start: La direccion {address} no tiene establecida una conexion. La establecemos.\n")
                    self.connections[address] = ServerProtocol(msg.data, self.server_socket, address)
                    self.connections[address].start()

                else:
                    if msg.message_type == MessageType.ACK:
                        #print(f"Server.start: Llega un ACK de '{address}'\n")
                        self.server_socket.acknowledge(msg.sequence_number, address)
                    else:
                        #print(f"Server.start: Guardamos el mensaje en la queue de '{address}'\n")
                        self.connections[address].queue.put(msg)
            except TimeoutError:
                pass
    
    def close_socket(self):
        self.server_socket.close()