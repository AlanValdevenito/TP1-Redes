from socket import *
import pickle
from threading import Event
from message import Message, MessageType

UPLOAD = 'upload'
DOWNLOAD = 'download'
ACKNOWLEDGE = 'ACK'

MAX_LENGTH = 4096
MAX_LENGTH_DATA = 2048 # Hay que contemplar los bytes de la estructura
EOF_MARKER = chr(26)

class SocketRDT:
    def __init__(self, ip, port, timeout):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.socket.settimeout(timeout)
        self.ack_events = {}
        self.sequence_number = 0 # sirve para un cliente, estaría bueno guardarlo en el protocolo mejor

    def listen(self):
        self.socket.bind((self.ip, self.port))

    def recv(self):
        msg, address = self.socket.recvfrom(MAX_LENGTH)
        msg_object = pickle.loads(msg)

        ack_msg = Message(MessageType.ACK, msg_object.sequence_number, None)
        self.socket.sendto(pickle.dumps(ack_msg), address)
        return msg_object, address

    def send(self, type, data, address): # considerar pasar sequence_number como param
        sent_bits = 0
        
        if not data.endswith(EOF_MARKER) and type == MessageType.DATA:
            data += EOF_MARKER
        
        len_message = len(data)

        while sent_bits < len_message:
            current_data = data[sent_bits:sent_bits+MAX_LENGTH_DATA]
            message = Message(type, self.sequence_number, current_data)
            try:
                self.socket.sendto(pickle.dumps(message), address)
                self.wait_acknowledge(self.sequence_number, address)   
                self.sequence_number += 1
                sent_bits += MAX_LENGTH_DATA
            except TimeoutError:
                continue
    
    def wait_acknowledge(self, sequence_number, address):
        event = Event()
        self.ack_events[(sequence_number, address)] = event
        if not event.wait(self.timeout): # bloqueo hasta recibir el evento de ack
            raise TimeoutError           # si event.wait() retorna false, hay timeout
        del self.ack_events[(sequence_number, address)] # elimino el evento del diccionario

    def acknowledge(self, seq, address):
        event = self.ack_events.get((seq, address))
        if event:
            event.set()
        
    def close(self):
        self.socket.close()