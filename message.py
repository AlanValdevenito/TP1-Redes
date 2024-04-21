from enum import Enum

class MessageType(Enum):
    

class Message:
    def __init__(self, type, sequence_number, data):
        self.type = type
        self.sequence_number = sequence_number