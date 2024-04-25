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
        self.file_name = "file name"

    # @classmethod
    def encode(self):
        file_name_bytes = self.file_name.encode().ljust(200, b'\0') if self.file_name else b'\0' * 200
        data_bytes = self.data.encode() if self.data else b'\0'
        bytes_arr = self.message_type.value.to_bytes(1, byteorder='big') + \
                    self.sequence_number.to_bytes(4, byteorder='big') + \
                    file_name_bytes + \
                    len(data_bytes).to_bytes(4, byteorder='big') + \
                    data_bytes
        return bytes_arr

    @classmethod
    def decode(cls, bytes_arr):
        message_type = MessageType(int.from_bytes(bytes_arr[0:1], byteorder='big'))
        sequence_number = int.from_bytes(bytes_arr[1:5], byteorder='big')
        file_name = bytes_arr[5:205].decode().rstrip('\0')
        data_length = int.from_bytes(bytes_arr[205:209], byteorder='big')
        data = bytes_arr[209:209 + data_length].decode()
        return cls(message_type, sequence_number, data)