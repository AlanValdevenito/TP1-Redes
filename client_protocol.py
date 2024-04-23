from socket import *
from threading import Thread
from socket_rdt import SocketRDT
from message import MessageType
import pickle

UPLOAD = 'upload'
DOWNLOAD = 'download'
MAX_LENGTH = 4096
EOF_MARKER = chr(26)
ACKNOWLEDGE = 'ACK'

class ClientProtocol:
    def __init__(self, ip, port, timeout):
        self.socket = SocketRDT(ip, port, timeout)
        self.address = (ip, port)

    def acknowledge(self):
        ack, address = self.socket.socket.recvfrom(MAX_LENGTH)
        msg = pickle.loads(ack)

        if msg.message_type == MessageType.ACK:
            self.socket.acknowledge(msg.sequence_number, address)
            return msg.sequence_number, address

        return -1, None

    def upload(self, message, file_name):
        try:
            th_1 = Thread(target = self.socket.send, args = (MessageType.INSTRUCTION, UPLOAD, self.address))
            th_2 = Thread(target = self.socket.send, args = (MessageType.FILE_NAME, file_name, self.address))
            th_3 = Thread(target = self.socket.send, args = (MessageType.DATA, message, self.address))
            
            th_1.start()
            self.acknowledge()
            th_1.join()

            th_2.start()
            self.acknowledge()
            th_2.join()

            th_3.start()
            self.acknowledge()
            th_3.join()
        except TimeoutError:
            print(f"Timeout")

    def download(self, name):
        th_1 = Thread(target = self.socket.send, args = (MessageType.INSTRUCTION, DOWNLOAD, self.address))
        th_2 = Thread(target = self.socket.send, args = (MessageType.FILE_NAME, name, self.address))

        th_1.start()
        self.acknowledge()
        th_1.join()

        th_2.start()
        self.acknowledge()
        th_2.join()
        
        data = b''
        next_sequence_number = 0
        while True:
            msg_obj, _ = self.socket.recv()

            if msg_obj.message_type != MessageType.DATA or msg_obj.sequence_number != next_sequence_number:
                continue

            data += msg_obj.data.encode()
            next_sequence_number = next_sequence_number + 1
            
            if data.endswith(EOF_MARKER.encode()): 
                break
        
        return data.decode(encoding="latin-1")[:-1]

    def close(self):
        self.socket.close()