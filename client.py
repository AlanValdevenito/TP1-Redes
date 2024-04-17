from socket_UDP import Socket

UPLOAD = 'upload'
DOWNLOAD = 'download'

class Client:
    def __init__(self, ip, port):
        self.socket = Socket(ip, port, 0, 2)
        self.ip = ip
        self.port = port
    
    def send(self, message):
        self.socket.send(message, (self.ip, self.port))

    def recv(self):
        return self.socket.recv()

    def upload(self, file_name):

        self.send(UPLOAD)

        with open(file_name, 'r') as f:
            message = f.read()
            self.send(message)

        self.close_socket()

    def download(self):
        self.send(DOWNLOAD)

        file, _ = self.recv()

        with open('result_download.txt', 'w') as f:
            f.write(file)

        self.close_socket()

    def close_socket(self):
        self.socket.close()