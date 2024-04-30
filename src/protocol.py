from socket import *
from message import *
import random
MAX_LENGTH = 64


from termcolor import colored # pa los print




class StopAndWaitProtocol:
    def __init__(self, ip, port):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.ip = ip
        self.port = port

    def listen(self):
        self.socket.bind((self.ip, self.port))
        print(f"socket bindeado en {(self.ip, self.port)}")

    def get_port(self):
        print(f"protocol.get_port() -> {self.socket.getsockname()[1]}")
        return self.socket.getsockname()[1]
    
    def recv(self):
        encoded_msg, address = self.socket.recvfrom(MAX_LENGTH * 2)
        msg = Message.decode(encoded_msg)
        #print(f"recvt msg.data = {msg.data}")
        #msg.print()
        return msg, address

    def send(self, request, address):
        #print(f"send: request.data = {request.data}")
        rdm = random.randint(0, 9)
        if rdm < 8:
            self.socket.sendto(request.encode(), address)
        else:
            print(colored("se perdio un send", "red"))


    # Recibe un Message y un address
    # manda el message de forma reliable
    def send_data(self, message, address):
        # print(f"sending data to address = {address}")
        encoded_msg = message.encode()
        msg_acked = False
        count = 0
        while not msg_acked:
            try:
                if count >= 10:
                    break
                rdm = random.randint(0, 9)
                if rdm < 5:
                    self.socket.sendto(encoded_msg, address)
                else:
                    # puede darse el caso de que el que esta mandando el archivo
                    # mande un END, el otro conteste con un ACK pero el ACK se pierde
                    # el que mando el ACK se desconecta
                    #
                    # Cuento cuantos END se perdieron. Si llega a 10
                    # es probable que el receiver se haya desconectado
                    # en tal caso salgo del send_data
                    if message.message_type == MessageType.END:
                        count += 1
                        print(colored("se perdio el END", "red"))
                    else:
                        print(colored("se perdio la data", "red"))
                self.socket.settimeout(0.05)
                msg_acked = self.recv_ack(message.sequence_number)
                
            except TimeoutError:
                continue
        self.socket.setblocking(True)


    # private
    # Recibe un ack, devuelve True si coincide el seq_number,
    # devuelve False en caso contrario
    def recv_ack(self, seq_number):
        encoded_msg, _ = self.socket.recvfrom(1024)
        msg = Message.decode(encoded_msg)
        if msg.sequence_number != seq_number:
            print(colored(f"NO COINCIDE EL SEQNUM. expected = {seq_number}, got = {msg.sequence_number}", "red"))
        return msg.sequence_number == seq_number
    
    # private
    # Manda un ACK para un seq_number dado
    def send_ack(self, seq_number, address):
        ack = Message(MessageType.ACK, seq_number, "")
        rdm = random.randint(0, 9)
        if rdm < 5:
            self.socket.sendto(ack.encode(), address)
        else:
            print(colored("se perdio el ack", "red"))
    
    # Recibe data, manda el correspondiente ACK y devuelve la data
    # en forma de Message
    def recv_data(self):
        encoded_msg, address = self.socket.recvfrom(1024)
        #self.socket.settimeout(0.1)
        msg = Message.decode(encoded_msg)
        self.send_ack(msg.sequence_number, address)
        return msg, address
    
    def close(self):
        self.socket.close()