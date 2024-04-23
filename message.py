from enum import Enum

class MessageType(Enum):
    INSTRUCTION = 1
    DATA = 2
    FILE_NAME = 3
    ACK = 4
    
class Message:
    def __init__(self, message_type, sequence_number, data):
        self.message_type = message_type
        self.sequence_number = sequence_number
        self.data = data
    