from threading import Thread
import queue

UPLOAD = 'upload'
DOWNLOAD = 'download'
EOF_MARKER = chr(26)

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
            # self.download()
            pass

    def upload(self):
        file_name = self.queue.get()
        file = b''

        while True:
            seq = self.queue.get()
            message = self.queue.get()

            file += message

            self.socket_server.send(ACKNOWLEDGE, self.client_address)

            if message.endswith(EOF_MARKER.encode()): 
                break

        file_decode = file.decode(encoding="latin-1")[:-1]
        print(file_decode)

        with open(file_name, 'w', encoding='latin-1') as f:
            f.write(file_decode)

        #self.close_socket()