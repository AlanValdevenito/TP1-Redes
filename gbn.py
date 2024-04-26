from socket import *
from threading import Event
from message import Message, MessageType

WINDOW_SIZE = 10

UPLOAD = 'upload'
DOWNLOAD = 'download'
MAX_LENGTH = 4096
MAX_LENGTH_DATA = 15 # Hay que contemplar los bytes de la estructura
EOF_MARKER = chr(26)
ACKNOWLEDGE = 'ACK'

class GBN:
    def __init__(self, ip, port, timeout):
        self.base = 0
        self.signumsec = 0
        self.n = WINDOW_SIZE
        self.highest_inorder_seqnum = 0

        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.address = (ip,port)
        self.timeout = timeout
        self.socket.settimeout(timeout)
        
    def listen(self):
        self.socket.bind((self.ip, self.port))

    def recv(self):
        encoded_msg, address = self.socket.recvfrom(MAX_LENGTH)
        decoded_msg = Message.decode(encoded_msg)

        if decoded_msg.message_type == MessageType.ACK:
            return decoded_msg, address

        if decoded_msg.sequence_number == self.highest_inorder_seqnum:  # Si el numero de secuencia recibido sigue el orden, manda ese ACK acumulativo.
            self.highest_inorder_seqnum += 1
            ack_msg = Message(MessageType.ACK, decoded_msg.sequence_number, None)
            self.socket.sendto(ack_msg.encode(), address)
            return decoded_msg, address
        
        # Si el packet esta fuera de orden, reenviamos el ACK del mayor numero de secuencia en orden registrado anteriormente. Descartar paquete?
        ack_msg = Message(MessageType.ACK, self.highest_inorder_seqnum, None)
        self.socket.sendto(ack_msg.encode(), address)
        
        return '', address

    def send(self, type, data, sequence_number):
        sent_bits = 0
        
        if type == MessageType.DATA and not data.endswith(EOF_MARKER):
            data += EOF_MARKER
    
        len_message = len(data)
                
        while sent_bits < len_message:
            if self.signumsec <= self.base + self.n - 1:
                current_data = data[sent_bits:sent_bits+MAX_LENGTH_DATA]
                message = Message(type, sequence_number, current_data)
                self.socket.sendto(message.encode(), self.address)
                self.signumsec += 1
                sequence_number += 1
                sent_bits += MAX_LENGTH_DATA

            else:
                try:
                    if self.is_server == True:
                        self.wait_acknowledge(sequence_number, self.address)    
                    else:
                        self.recv_acknowledge()
                    
                except TimeoutError:
                    continue
            
        return sequence_number
    
    def recv_acknowledge(self):
        encoded_ack, address = self.socket.recvfrom(MAX_LENGTH)
        msg = Message.decode(encoded_ack)

        if msg.message_type != MessageType.ACK:
            return -1, None
        
        if msg.sequence_number > self.base:
            self.base = msg.sequence_number + 1

        return msg.sequence_number, address

    def wait_acknowledge(self, sequence_number, address):
        event = Event()
        self.ack_events[(sequence_number, address)] = event
        if not event.wait(self.timeout):
            raise TimeoutError
        del self.ack_events[(sequence_number, address)]

    def acknowledge(self, seq, address):
        while True:
            event = self.ack_events.get((seq, address))
            if event:
                event.set()
                return

    def close(self):
        self.socket.close()