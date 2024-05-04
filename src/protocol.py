from abc import ABC, abstractmethod
from socket import *
from message import Message, MessageType
from config import MAX_LENGTH


class Protocol(ABC):
    def __init__(self, ip, port, logger):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.ip = ip
        self.port = port
        self.logger = logger

    def listen(self):
        self.socket.bind((self.ip, self.port))
        self.logger.log(f"Socket bindeado en {self.socket.getsockname()}\n")

    def get_port(self):
        return self.socket.getsockname()[1]

    def recv(self):
        encoded_msg, address = self.socket.recvfrom(MAX_LENGTH * 2)
        decoded_msg = Message.decode(encoded_msg)
        # print(colored(f"Receiving {decoded_msg}\nfrom {address}\n", "green"))
        return decoded_msg, address

    def send(self, request, address):
        self.socket.sendto(request.encode(), address)
        # print(colored(f"Sending {request}\nto {address}\n", "green"))

    @abstractmethod
    def send_data(self, message, address):
        pass

    @abstractmethod
    def recv_data(self):
        pass

    def send_end(self, sequence_number, address):
        self.logger.log("Enviamos END")
        end_message = Message(MessageType.END, sequence_number, "")
        self.socket.sendto(end_message.encode(), address)
        self.socket.setblocking(True)
        self.socket.settimeout(1)
        try:
            end_ack, _ = self.recv()
            if end_ack.message_type == MessageType.ACK_END:
                self.logger.log("Recibimos ACK del END\n")
        except TimeoutError:
            self.logger.log("Esperamos el ACK del END, pero no llegó")
            self.socket.sendto(end_message.encode(), address)

    def wait_end(self, sequence_number, address):
        self.logger.log("Esperamos waiting END")
        self.socket.setblocking(True)
        fin, _ = self.recv()
        self.logger.log("Recibimos END\n")
        self.socket.sendto(Message(MessageType.ACK_END, sequence_number, "").encode(), address)

    def close(self):
        self.socket.close()

    def __str__(self):
        return type(self).__name__
