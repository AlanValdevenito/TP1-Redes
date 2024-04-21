from threading import Thread
import queue

UPLOAD = 'upload'
DOWNLOAD = 'download'
EOF_MARKER = chr(26)
MAX_LENGTH = 10
ACKNOWLEDGE = 'ACK'

class Session:
    def __init__(self, type, socket_server, address):
        self.type = type
        self.state = 0
        self.socket_server= socket_server
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
            pass
    
    def download(self):
        file_name = self.queue.get()

        with open(file_name, 'r', encoding='latin-1') as file:
            message = file.read()

        if not message.endswith(EOF_MARKER):
            message += EOF_MARKER

        len_message = len(message)
        sent_bits = 0
        sequence_number = 0

        while sent_bits < len_message:
            current_message = message[sent_bits:sent_bits+MAX_LENGTH]
            self.socket_server.send(sequence_number.to_bytes(4, 'big', signed=False), self.client_address)
            self.socket_server.send(current_message.encode(), self.client_address)
            acknowledge = self.queue.get()
            
            if acknowledge.decode() == ACKNOWLEDGE:
                sent_bits += MAX_LENGTH
                sequence_number += 1

    def upload(self):
        file_name = self.queue.get()
        file = b''

        while True:
            seq = self.queue.get()
            message = self.queue.get()
            file += message
            self.socket_server.send(ACKNOWLEDGE.encode(), self.client_address)

            if message.endswith(EOF_MARKER.encode()): 
                break

        file_decode = file.decode(encoding="latin-1")[:-1]
        print(file_decode)

        with open(file_name, 'w', encoding='latin-1') as f:
            f.write(file_decode)

        #self.close_socket()