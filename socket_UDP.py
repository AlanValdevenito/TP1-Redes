from socket import *
import random

EOF_MARKER = chr(26)
MAX_LENGTH = 10 # Envia/recibe MAX_LENGTH bits como maximo

ACKNOWLEDGE = 'ACK'

class Socket:
    def __init__(self, ip, port, protocol, timeout):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.ip = ip
        self.port = port
        self.socket.settimeout(timeout)
        self.protocol = protocol
        
    def listen(self):
        self.socket.bind((self.ip, self.port))

    def send(self, message, address):
        if not message.endswith(EOF_MARKER):
            message += EOF_MARKER

        len_message = len(message)
        sent_bits = 0
        sequence_number = 0
        while sent_bits < len_message:
            current_message = message[sent_bits:sent_bits+MAX_LENGTH]
            
            try:
                print(f"send msg: {current_message}")
                print(f"send seq: {sequence_number}")
                self.socket.sendto(sequence_number.to_bytes(4, 'big', signed=False), address)
                self.socket.sendto(current_message.encode(), address)
                acknowledge, address = self.socket.recvfrom(MAX_LENGTH)
                print(acknowledge)
                if acknowledge.decode() == ACKNOWLEDGE:
                    sent_bits += MAX_LENGTH

                sequence_number += 1

            except TimeoutError:
                print(f"Timeout")
                continue

    def recv(self):
        data = b''
        previous_sequence_number = -1
        while True:
            sequence_number, address = self.socket.recvfrom(4)
            message, address = self.socket.recvfrom(MAX_LENGTH)
            print(f"recv msg: {message}")
            print(f"recv seq: {sequence_number}")
            if sequence_number != previous_sequence_number:
                data += message

            rdm = random.randint(0, 9)
            if rdm > 8:
                continue
            
            previous_sequence_number = sequence_number
            self.socket.sendto(ACKNOWLEDGE.encode(), address)
            
            if message.endswith(EOF_MARKER.encode()): 
                break
        
        return data.decode()[:-1], address
    

    def close(self):
        self.socket.close()