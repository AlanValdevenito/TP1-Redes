from enum import Enum

class MessageType(Enum):
    INSTRUCTION = 1
    DATA = 2
    FILE_NAME = 3
    ACK = 4
    PORT = 5  # para mandarle el puerto al cliente
    END = 6   # para avisar que termine de mandar el archivo

class Message:
    def __init__(self, message_type, sequence_number, data):
        self.message_type = message_type
        self.sequence_number = sequence_number
        self.data = data
        self.file_name = "-"

    def print(self):
        
        print(f"message_type = {self.message_type}")
        print(f"sequence_number = {self.sequence_number}")
        print(f"data = {self.data}")
        print(f"file_name = {self.file_name}")
        print("--------------------------\n\n")
        
    def encode(self):
        file_name_bytes = self.file_name.encode().ljust(10, b'\0') if self.file_name else b'\0' * 10
        data_bytes = self.data.encode()
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
        file_name = bytes_arr[5:15].decode().rstrip('\0')
        data_length = int.from_bytes(bytes_arr[15:19], byteorder='big')
        data = bytes_arr[19:19 + data_length].decode()
        return Message(message_type, sequence_number, data)
