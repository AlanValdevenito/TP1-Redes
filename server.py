from socket_UDP import Socket

MAX_LENGTH = 10 # Envia/recibe MAX_LENGTH bits como maximo
UPLOAD = 'upload'
DOWNLOAD = 'download'
ACKNOWLEDGE = 'ACK'
EOF_MARKER = chr(26)


class Server:
    def __init__(self, ip, port, protocol):
        self.port = port
        self.server_socket = Socket(ip, port, protocol, 10)

    def start(self):
        self.server_socket.listen()

        type, _ = self.recv()

        self.process_request(type)

    def process_request(self, request_type):
        if request_type == UPLOAD:
            self.upload()
        elif request_type == DOWNLOAD:
            self.download()

    def send(self, message, address):
        self.server_socket.send(message, address)

    def recv(self):
        return self.server_socket.recv()
    
    def close_socket(self):
        self.server_socket.close()

    def upload(self):
        file_name, _ = self.recv()
        file, _ = self.recv()

        with open(file_name, 'w', encoding='latin-1') as f:
          f.write(file)

        self.close_socket()
    
    def download(self):
      file_name, clientAddress = self.recv()
      with open(file_name, 'r', encoding='latin-1') as file:
            message = file.read()
            self.send(message, clientAddress)

      self.close_socket()