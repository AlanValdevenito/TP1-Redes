from socket import *
import random

EOF_MARKER = chr(26)
MAX_LENGTH = 128 # Envia/recibe MAX_LENGTH bits como maximo

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
                # print(f"\nsend msg: {current_message}")
                print(f"\nsend seq: {sequence_number}")

                rdm = random.randint(0, 9)
                if rdm < 8:
                    self.socket.sendto(sequence_number.to_bytes(4, 'big', signed=False), address)
                else:
                    print("Se pierde el numero de secuencia")
            
                self.socket.sendto(current_message.encode(), address)
                acknowledge, address = self.socket.recvfrom(MAX_LENGTH)
                if acknowledge.decode() == ACKNOWLEDGE:
                    sent_bits += MAX_LENGTH

                sequence_number += 1

            except TimeoutError:
                print(f"Timeout")
                continue

    def recv(self):
        data = b''
        next_sequence_number = 0
        while True:
            sequence_number, address = self.socket.recvfrom(4)

            if sequence_number != next_sequence_number.to_bytes(4, 'big', signed=False):
                print(f"recv seq: {int.from_bytes(sequence_number, 'big', signed=False)}")
                print(f"recv nex seq: {next_sequence_number}\n")
                continue

            message, address = self.socket.recvfrom(MAX_LENGTH)

            next_sequence_number = next_sequence_number + 1
            data += message

            print(f"recv seq: {int.from_bytes(sequence_number, 'big', signed=False)}")
            print(f"recv nex seq: {next_sequence_number}\n")

            """rdm = random.randint(0, 9)
            if rdm > 8:
                print("Se pierde el ACK")
                continue"""
            
            self.socket.sendto(ACKNOWLEDGE.encode(), address)
            
            if message.endswith(EOF_MARKER.encode()): 
                break
        
        return data.decode(encoding="latin-1")[:-1], address
    

    def close(self):
        self.socket.close()