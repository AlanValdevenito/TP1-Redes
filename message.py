from enum import Enum

class MessageType(Enum):
    ACK = 1
    DATA = 2
    FILE_NAME = 3

class Message:
    def __init__(self, message_type, sequence_number, data, source_address):
        self.message_type = message_type
        self.sequence_number = sequence_number
        self.data = data
        self.source_address = source_address
    