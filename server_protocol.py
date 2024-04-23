from threading import Thread
import queue
from message import MessageType

UPLOAD = 'upload'
DOWNLOAD = 'download'
EOF_MARKER = chr(26)
MAX_LENGTH = 10
ACKNOWLEDGE = 'ACK'

class ServerProtocol:
    def __init__(self, type, socket_server, address):
        self.type = type
        self.state = 0
        self.socket_server = socket_server
        self.client_address = address
        self.queue = queue.Queue()

    def start(self):
        sessionThread = Thread(target = self.handle_client)
        sessionThread.start()

    def push(self, msg):
        self.queue.put(msg)
        
    def handle_client(self):
        if self.type == UPLOAD:
            self.upload()
        elif self.type == DOWNLOAD:
            self.download()
    
    def download(self):
        file_name = self.queue.get().data

        with open(file_name, 'r', encoding='latin-1') as file:
            message = file.read()
        
        self.socket_server.send(MessageType.DATA, message, self.client_address)

    def upload(self):
        file_name_msg = self.queue.get()
        file_name = file_name_msg.data
        next_sequence_number = file_name_msg.sequence_number + 1

        data = b''
        while True:
            current_msg = self.queue.get()
            if current_msg.sequence_number != next_sequence_number:
                continue

            next_sequence_number = next_sequence_number + 1
            data += current_msg.data.encode()

            if data.endswith(EOF_MARKER.encode()): 
                break

        file = data.decode(encoding="latin-1")[:-1]

        with open(file_name, 'w', encoding='latin-1') as f:
            f.write(file)