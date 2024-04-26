from socket import *
from threading import Thread
import threading
from socket_rdt import SocketRDT
from message import MessageType
from message import Message

UPLOAD = 'upload'
DOWNLOAD = 'download'
MAX_LENGTH = 4096
EOF_MARKER = chr(26)
ACKNOWLEDGE = 'ACK'

class ClientProtocol:
    def __init__(self, ip, port, timeout):
        self.socket = SocketRDT(ip, port, timeout, False)
        self.address = (ip, port)
        self.sequence_number = 0

    """
    def acknowledge(self):
        encoded_ack, address = self.socket.socket.recvfrom(MAX_LENGTH)
        # msg = pickle.loads(ack)
        msg = Message.decode(encoded_ack)

        if msg.message_type == MessageType.ACK:
            print(f"ClientProtocol.acknowledge ({threading.current_thread().name}) - (5): Enviamos un ACK")
            self.socket.acknowledge(msg.sequence_number, address) #
            return msg.sequence_number, address

        return -1, None

    def wait_for_acks(self, n):
        i = 0
        while i < n:
            try:
                self.acknowledge()
                i+=1
            except TimeoutError:
                print("Timeout esperando ack")
    """

    def upload(self, message, file_name):
        self.sequence_number = self.socket.send(MessageType.INSTRUCTION, UPLOAD, self.address, self.sequence_number)
        self.sequence_number = self.socket.send(MessageType.FILE_NAME, file_name, self.address, self.sequence_number)
        self.sequence_number = self.socket.send(MessageType.DATA, message, self.address, self.sequence_number)

        """try:
            th_ack = Thread(target = self.wait_for_acks, args = (3,)) # esto está mal xq a lo mejor el send de data toma
                                                                      # mas de un mensaje
            
            th_ack.start()

            self.sequence_number = self.socket.send(MessageType.INSTRUCTION, UPLOAD, self.address, self.sequence_number)
            
            self.sequence_number = self.socket.send(MessageType.FILE_NAME, file_name, self.address, self.sequence_number)
            self.sequence_number = self.socket.send(MessageType.DATA, message, self.address, self.sequence_number)
            
            th_ack.join()

        except TimeoutError:
            print(f"Timeout")"""

    def download(self, name):
        print("ClientProtocol.download: Enviando DOWNLOAD\n")
        self.sequence_number = self.socket.send(MessageType.INSTRUCTION, DOWNLOAD, self.address, self.sequence_number)
        print("ClientProtocol.download: Enviando el nombre del archivo\n")
        self.sequence_number = self.socket.send(MessageType.FILE_NAME, name, self.address, self.sequence_number)
        
        data = b''
        next_sequence_number = 0 #
        while True:
            try:
                msg_obj, _ = self.socket.recv()
                print(f"ClientProtocol.download: Recibimos {msg_obj.data}")

                if msg_obj.message_type != MessageType.DATA or msg_obj.sequence_number != next_sequence_number:
                    continue

                data += msg_obj.data.encode()
                next_sequence_number = next_sequence_number + 1
                
                if data.endswith(EOF_MARKER.encode()): 
                    break
                
            except TimeoutError:
                print("Timeout")
        
        return data.decode(encoding="latin-1")[:-1]

    def close(self):
        self.socket.close()