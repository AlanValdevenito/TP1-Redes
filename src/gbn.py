from socket import *
from message import Message, MessageType
from termcolor import colored 
import random

WINDOW_SIZE = 3
MAX_LENGTH = 64

class GBN:
    def __init__(self, ip, port):
        self.base = 0
        self.signumsec = 0
        self.n = WINDOW_SIZE
        self.highest_inorder_seqnum = 0

        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.address = (ip,port)
        self.timeout = timeout
        self.socket.settimeout(0.0001)

        self.messages = {}
        
    def listen(self):
        self.socket.bind(self.address)
        print(f"Socket bindeado en {self.address}\n")

    def get_port(self):
        return self.socket.getsockname()[1]

    def recv_data(self):
        self.socket.setblocking(True)
        encoded_msg, address = self.socket.recvfrom(MAX_LENGTH*2)
        decoded_msg = Message.decode(encoded_msg)
        print(colored(f"Receiving {decoded_msg}\nfrom {address}\n", "green"))

        if (decoded_msg.message_type == MessageType.ACK): # or (decoded_msg.message_type == MessageType.END): \
            #or (decoded_msg.message_type == MessageType.INSTRUCTION) \
            #or (decoded_msg.message_type == MessageType.FILE_NAME):
            return decoded_msg, address
        
        if (decoded_msg.message_type == MessageType.END):
            self.send_ack(decoded_msg.sequence_number, address)
            return decoded_msg, address

        if decoded_msg.message_type == MessageType.ACK:
            if decoded_msg.sequence_number < self.base:
                return decoded_msg, address
            print(f"Llega un ACK con numero de secuencia {decoded_msg.sequence_number}. Aumentamos la base.\n")
            self.base = decoded_msg.sequence_number + 1

        if decoded_msg.sequence_number == self.highest_inorder_seqnum:  # Si el numero de secuencia recibido sigue el orden, manda ese ACK acumulativo.
            self.highest_inorder_seqnum += 1
            self.send_ack(decoded_msg.sequence_number, address)
            return decoded_msg, address
        
        # Si el packet esta fuera de orden, reenviamos el ACK del mayor numero de secuencia en orden registrado anteriormente. Descartar paquete?
        # Me quedo esperando hasta que llegue el paquete ordenado
        while decoded_msg.sequence_number != self.highest_inorder_seqnum:
            self.send_ack(self.highest_inorder_seqnum, address)
            encoded_msg, address = self.socket.recvfrom(MAX_LENGTH*2)
            decoded_msg = Message.decode(encoded_msg)
        
        self.send_ack(decoded_msg.sequence_number, address)
        return decoded_msg, address
        #self.send_ack(self.highest_inorder_seqnum, address)
        #return '', address

    def send_ack(self, seq_number, address):
        """
        Envia un ACK.

        Parametros:
        - seq_number: Numero de secuencia del ultimo mensaje recibido.
        - address: Direccion a donde se debe enviar el ACK.
        """

        ack = Message(MessageType.ACK, seq_number, "")
        self.socket.sendto(ack.encode(), address)

    def send_data(self, message, address):
        
        print(f"n: {self.n}, base: {self.base}, signumsec: {self.signumsec}\n")
        if self.signumsec <= self.base + self.n - 1:
            print(colored(f"Sending {message}\nto {address}\n", "green"))
            encoded_msg = message.encode()              
            self.socket.sendto(encoded_msg, address)
            self.messages[self.signumsec] = encoded_msg
            self.signumsec += 1
            self.socket.setblocking(True)
            # comenzar timer para el paquete actual.
            # self.recv_ack(self.base) # Esto no deberia hacerse aca, deberia hacerse en el recv?

        else:
            print(colored("Se intento enviar un mensaje pero la ventana esta llena", "red"))

        """else:
            self.socket.setblocking(True) # ?
            while not self.recv_ack(self.base):
                if timer == 0:
                    for i in range(self.base, self.signumsec):
                        self.socket.sendto(self.messages[i], self.address)"""

    def recv_ack(self, seq_number):
        try:   
            encoded_msg, _ = self.socket.recvfrom(MAX_LENGTH * 2)
            msg = Message.decode(encoded_msg)

            if msg.sequence_number < seq_number:
                return False

            print(f"Llega un ACK con numero de secuencia {msg.sequence_number}. Aumentamos la base.\n")
            self.base = msg.sequence_number + 1
            return True
        except BlockingIOError:
            pass

    def retransmitir_paquetes(self, address):
        temp = self.base
        while temp < self.signumsec:
            encoded_msg = self.messages[temp]
            self.socket.sendto(encoded_msg, address)
            # Comenzar timer para este paquete
            temp += 1
    
    def close(self):
        self.socket.close()
