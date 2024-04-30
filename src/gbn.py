from socket import *
from message import Message, MessageType
from termcolor import colored 
import random
import time


WINDOW_SIZE = 3
MAX_LENGTH = 64

class GBN:
    def __init__(self, ip, port):
        self.base = 0
        self.signumsec = 0
        self.n = WINDOW_SIZE
        self.highest_inorder_seqnum = 0
        self.lastackreceived = 0
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.ip = ip
        self.port = port
        #self.address = (ip,port)
        self.timeout = timeout
        self.socket.settimeout(0.0001)
        self.allows_duplicates = False
        self.messages = {}

        #self.client_address = client_address

    def recv(self):
        encoded_msg, address = self.socket.recvfrom(MAX_LENGTH * 2)
        msg = Message.decode(encoded_msg)
        #print(f"recvt msg.data = {msg.data}")
        #msg.print()
        return msg, address

    def send(self, request, address):
        #print(f"send: request.data = {request.data}")
        rdm = random.randint(0, 9)
        #if rdm < 8:
        self.socket.sendto(request.encode(), address)
        #else:
        #    print(colored(f"Lost {request}\nto {address}\n", "red"))


    def listen(self):
        self.socket.bind((self.ip, self.port))
        print(f"Socket bindeado en {(self.ip, self.port)}\n")

    def allow_duplicates(self):
        self.allows_duplicates = True

    def get_port(self):
        return self.socket.getsockname()[1]

    def recv_data(self):
        #self.socket.setblocking(True)

        encoded_msg, address = self.socket.recvfrom(MAX_LENGTH*2)
        decoded_msg = Message.decode(encoded_msg)
        print(colored(f"Receiving {decoded_msg}\nfrom {address}\n", "green"))

        if decoded_msg.message_type == MessageType.ACK:
            if decoded_msg.sequence_number < self.base:
                return decoded_msg, address
            
            print(f"Llega un ACK con numero de secuencia {decoded_msg.sequence_number}. Aumentamos la base.\n")
            self.base = decoded_msg.sequence_number + 1
            return decoded_msg, address
        
        # if decoded_msg.sequence_number == self.highest_inorder_seqnum:  # Si el numero de secuencia recibido sigue el orden, manda ese ACK acumulativo.
        #    self.highest_inorder_seqnum += 1

        self.send_ack(decoded_msg.sequence_number, address)
        return decoded_msg, address
        
        """if (decoded_msg.message_type == MessageType.END):
            self.send_ack(decoded_msg.sequence_number, self.client_address)
            return decoded_msg, self.client_address

        if decoded_msg.message_type == MessageType.ACK:
            print("A")
            if decoded_msg.sequence_number < self.base:
                return decoded_msg, self.client_address
            print(f"Llega un ACK con numero de secuencia {decoded_msg.sequence_number}. Aumentamos la base.\n")
            self.base = decoded_msg.sequence_number + 1

        if decoded_msg.sequence_number == self.highest_inorder_seqnum:  # Si el numero de secuencia recibido sigue el orden, manda ese ACK acumulativo.
            self.highest_inorder_seqnum += 1
            self.send_ack(decoded_msg.sequence_number, self.client_address)
            return decoded_msg, self.client_address
        
        # Si el packet esta fuera de orden, reenviamos el ACK del mayor numero de secuencia en orden registrado anteriormente. Descartar paquete?
        # Me quedo esperando hasta que llegue el paquete ordenado
        while decoded_msg.sequence_number != self.highest_inorder_seqnum:
            self.send_ack(self.highest_inorder_seqnum, self.client_address)
            encoded_msg, self.client_address = self.socket.recvfrom(MAX_LENGTH*2)
            decoded_msg = Message.decode(encoded_msg)

        self.send_ack(decoded_msg.sequence_number, self.client_address)
        return decoded_msg, self.client_address
        #self.send_ack(self.highest_inorder_seqnum, self.client_address)
        #return '', self.client_address"""

    def send_ack(self, seq_number, address):
        """
        Envia un ACK.

        Parametros:
        - seq_number: Numero de secuencia del ultimo mensaje recibido.
        - address: Direccion a donde se debe enviar el ACK.
        """

        ack = Message(MessageType.ACK, seq_number, "")
        self.socket.sendto(ack.encode(), address)
        print(colored(f"Se envia el ACK a {address} con el numero de secuencia {seq_number}\n", "yellow"))
        
        """rdm = random.randint(0, 9)
        if rdm < 5:
            self.socket.sendto(ack.encode(), address)
            print(colored(f"Se envia el ACK a {address} con el numero de secuencia {seq_number}\n", "yellow"))
        else:
            print(colored("Se perdio un ACK", "red"))"""

    def send_data(self, message, address):
        #self.lastackreceived = time.time()
        print(f"n: {self.n}, base: {self.base}, signumsec: {self.signumsec}\n")
        encoded_msg = message.encode()
        
        #try:
        if self.signumsec <= self.base + self.n - 1:
            print(colored(f"Sending {message}\nto {address}\n", "green"))            
            self.socket.sendto(encoded_msg, address)

            """rdm = random.randint(0, 9)
            if rdm < 5:
                print(colored(f"Sending {message}\nto {address}\n", "green"))            
                self.socket.sendto(encoded_msg, address)
            else:
                print(colored(f"Lost {message}\nto {address}\n", "red"))"""
            
            self.messages[self.signumsec] = encoded_msg
            self.signumsec += 1
            # Comenzar timer para el paquete actual.
            self.socket.setblocking(False)
            self.recv_ack(self.base)

        else:
            print(colored("Ventana llena", "red"))
            print(colored(f"Lost {message}\nto {address}\n", "red"))
            # self.socket.settimeout(0.1)
            self.socket.setblocking(True)
            if self.recv_ack(self.base):
                print(colored(f"Sending {message}\nto {address}\n", "green"))
                self.socket.sendto(encoded_msg, address)
                self.messages[self.signumsec] = encoded_msg
                self.signumsec += 1

                #"""self.socket.setblocking(True)
                
                #while not self.recv_ack(self.base):
                #    if timer == 0:
                #        for i in range(self.base, self.signumsec):
                #            self.socket.sendto(self.messages[i], self.address)"""

            #if message.message_type == MessageType.END:
            #    print("Llega END, mandamos todos")
            #    while self.signumsec != self.base:
            #        self.recv_ack(self.base)
            #         if(time.time()-self.lastackreceived > 0.01):
            #            for i in range(self.base, self.signumsec):
            #                    self.socket.sendto(self.messages[i], self.address)
                            
        # except TimeoutError:
        #    print("Timeout")
        #    if(time.time()-self.lastackreceived > 0.01):
        #        for i in range(self.base, self.signumsec):
        #                    self.socket.sendto(self.messages[i], address)

    def recv_ack(self, seq_number):
        try:   
            encoded_msg, _ = self.socket.recvfrom(MAX_LENGTH * 2)
            msg = Message.decode(encoded_msg)

            print(colored(f"Llega un ACK con numero de secuencia {msg.sequence_number}.", "yellow"))

            if msg.sequence_number < seq_number:
                print(colored(f"No aumentamos la base.\n", "yellow"))
                return False

            print(colored(f"Aumentamos la base.\n", "yellow"))
            self.base = msg.sequence_number + 1
            # self.lastackreceived = time.time()
            return True
        
        except BlockingIOError:
            pass
    
    def close(self):
        self.socket.close()