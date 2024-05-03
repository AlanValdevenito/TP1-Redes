from socket import *
from message import Message

MAX_LENGTH = 1024


class Protocol:
    def __init__(self, ip, port):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.ip = ip
        self.port = port

    def listen(self):
        self.socket.bind((self.ip, self.port))
        print(f"Socket bindeado en {self.socket.getsockname()}")

    def get_port(self):
        return self.socket.getsockname()[1]

    def recv(self):
        encoded_msg, address = self.socket.recvfrom(MAX_LENGTH * 2)
        decoded_msg = Message.decode(encoded_msg)
        # print(colored(f"Receiving {decoded_msg}\nfrom {address}\n", "green"))
        return decoded_msg, address

    def close(self):
        self.socket.close()

    def __str__(self):
        return type(self).__name__
