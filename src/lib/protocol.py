from abc import ABC, abstractmethod
from socket import socket, AF_INET, SOCK_DGRAM
from .message import Message, MessageType
from .config import MAX_LENGTH
from enum import Enum


class EndState(Enum):
    NOT_STARTED = 0
    END_SENT = 1
    RECV_END_ACK = 2
    TIME_WAIT = 3
    CLOSE_WAIT = 4
    LAST_ACK = 5
    CLOSED = 6


class Protocol(ABC):
    def __init__(self, ip, port, logger):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.ip = ip
        self.port = port
        self.logger = logger
        self.end_state = EndState.NOT_STARTED

    def listen(self):
        self.socket.bind((self.ip, self.port))
        self.logger.log(f"Server listening on {self.socket.getsockname()}\n")

    def get_port(self):
        return self.socket.getsockname()[1]

    def recv(self):
        encoded_msg, address = self.socket.recvfrom(MAX_LENGTH * 2)
        decoded_msg = Message.decode(encoded_msg)
        return decoded_msg, address

    def send(self, request, address):
        self.socket.sendto(request.encode(), address)

    @abstractmethod
    def send_data(self, message, address):
        pass

    @abstractmethod
    def recv_data(self):
        pass

    def send_end(self, sequence_number, address):
        end_message = Message(MessageType.END, sequence_number, "")
        self.logger.log(f"Sending END\n")
        self.socket.sendto(end_message.encode(), address)
        self.socket.setblocking(True)
        self.socket.settimeout(1)
        ack_arrived = False
        count = 0
        while not ack_arrived and count < 10:
            try:
                self.socket.sendto(end_message.encode(), address)
                end_ack, _ = self.recv()
                if end_ack.message_type == MessageType.ACK_END:
                    self.logger.log("Receiving ACK-END\n")
                    if self.end_state == EndState.END_SENT:
                        self.end_state = EndState.RECV_END_ACK
                    else:
                        self.end_state = EndState.LAST_ACK
                    ack_arrived = True
                if (end_ack.message_type == MessageType.END
                        and self.end_state == EndState.END_SENT):
                    self.logger.log("END received. No need to wait for ACK.")
                    self.socket.sendto(Message(
                        MessageType.ACK_END, sequence_number, "").encode(),
                        address)
                    self.end_state = EndState.TIME_WAIT
                    ack_arrived = True
            except TimeoutError:
                self.logger.log(f"Re-sending END to {address}\n")
                if self.end_state == EndState.CLOSE_WAIT:
                    ack = Message(MessageType.ACK_END, sequence_number, "")
                    self.socket.sendto(ack.encode(), address)
                else:
                    self.socket.sendto(end_message.encode(), address)
                count += 1
                continue

    def wait_end(self, sequence_number, address):
        self.logger.log("Waiting END\n")
        if self.end_state == EndState.TIME_WAIT:
            self.end_state = EndState.CLOSED
            return
        self.socket.setblocking(True)
        self.socket.settimeout(3)
        try:
            fin, _ = self.recv()
            self.logger.log("Receiving END\n")
            self.logger.log(f"Sending ACK-END to {address}\n")
            self.socket.sendto(Message(
                MessageType.ACK_END, sequence_number, "").encode(), address)
        except TimeoutError:
            self.logger.log(
                "Timed out while waiting"
                f" for END for address {address}")
            pass
        self.end_state = EndState.CLOSED

    def close(self):
        self.socket.close()

    def __str__(self):
        return type(self).__name__
