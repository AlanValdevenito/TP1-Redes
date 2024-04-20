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

    def upload(self, file_name, src):
        self.send(UPLOAD)
        self.send(file_name)

        with open(src, 'r', encoding='latin-1') as f:
            message = f.read()
            print(message)
            self.send(message)

        self.close_socket()

    def download(self, name, dst):
        self.send(DOWNLOAD)
        self.send(name)

        file, _ = self.recv()

        with open(dst, 'w', encoding='latin-1') as f:
            f.write(file)

        self.close_socket()

    def close_socket(self):
        self.socket.close()