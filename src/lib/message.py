from enum import Enum


class MessageType(Enum):
    INSTRUCTION = 1
    DATA = 2
    ERROR = 3
    ACK = 4
    PORT = 5
    END = 6
    ACK_END = 7


class Message:
    def __init__(self, message_type, sequence_number, data, file_name=""):
        self.message_type = message_type
        self.sequence_number = sequence_number
        self.data = data
        self.file_name = file_name

    def encode(self):
        file_name_bytes = (self.file_name.encode().ljust(20, b'\0')
                           if self.file_name else b'\0' * 20)
        data_bytes = self.data
        if isinstance(self.data, str):
            data_bytes = self.data.encode()
        bytes_arr = self.message_type.value.to_bytes(1, byteorder='big') + \
            self.sequence_number.to_bytes(4, byteorder='big') + \
            file_name_bytes + \
            len(data_bytes).to_bytes(4, byteorder='big') + \
            data_bytes

        return bytes_arr

    @classmethod
    def decode(cls, bytes_arr):
        message_type = MessageType(
            int.from_bytes(bytes_arr[0:1], byteorder='big'))
        sequence_number = int.from_bytes(bytes_arr[1:5], byteorder='big')
        file_name = bytes_arr[5:25].decode().rstrip('\0')
        data_length = int.from_bytes(bytes_arr[25:29], byteorder='big')
        data = bytes_arr[29:29 + data_length]
        if message_type != MessageType.DATA:
            data = data.decode()
        return Message(message_type, sequence_number, data, file_name)

    def __str__(self):
        return f"\n--------------------------\
                \nmessage_type = {self.message_type}\
                \nsequence_number = {self.sequence_number}\
                \nfile_name = {self.file_name}\
                \n--------------------------"
