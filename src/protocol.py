from abc import ABC, abstractmethod
from socket import *
from message import Message, MessageType

MAX_LENGTH = 64


class Protocol(ABC):
    def __init__(self, ip, port):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.ip = ip
        self.port = port

    def listen(self):
        self.socket.bind((self.ip, self.port))
        print(f"Socket bindeado en {self.socket.getsockname()}\n")

    def get_port(self):
        return self.socket.getsockname()[1]

    def recv(self):
        encoded_msg, address = self.socket.recvfrom(MAX_LENGTH * 2)
        decoded_msg = Message.decode(encoded_msg)
        # print(colored(f"Receiving {decoded_msg}\nfrom {address}\n", "green"))
        return decoded_msg, address

    @abstractmethod
    def send_data(self, message, address):
        pass

    @abstractmethod
    def recv_data(self):
        pass

    def send_end(self, sequence_number, address):
        print("Enviamos END")
        end_message = Message(MessageType.END, sequence_number, "")
        self.socket.sendto(end_message.encode(), address)
        self.socket.setblocking(True)
        self.socket.settimeout(1)
        try:
            end_ack, _ = self.recv()
            if end_ack.message_type == MessageType.ACK_END:
                print("Recibimos ACK del END\n")
        except TimeoutError:
            print("Esperamos el ACK del END, pero no llegó")
            self.socket.sendto(end_message.encode(), address)

    def wait_end(self, sequence_number, address):
        print("Esperamos waiting END")
        self.socket.setblocking(True)
        fin, _ = self.recv()
        print("Recibimos END\n")
        self.socket.sendto(Message(MessageType.ACK_END, sequence_number, "").encode(), address)

    def close(self):
        self.socket.close()

    def __str__(self):
        return type(self).__name__
