from socket import *

MAX_LENGTH = 10

class ServerProtocol:
    def __init__(self, ip, port, protocol, timeout):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.ip = ip
        self.port = port
        self.protocol = protocol

    def listen(self):
        self.socket.bind((self.ip, self.port))

    def recv(self):
        return self.socket.recvfrom(MAX_LENGTH)

    def send(self, msg, address):
        self.socket.sendto(msg.encode(), address)

    def close(self):
        self.socket.close()