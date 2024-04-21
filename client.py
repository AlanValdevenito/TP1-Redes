from client_protocol import ClientProtocol

class Client:
    def __init__(self, ip, port):
        self.socket = ClientProtocol(ip, port, 0, 2)
        self.ip = ip
        self.port = port
    
    def send(self, message):
        self.socket.send(message, (self.ip, self.port))

    def recv(self):
        return self.socket.recv()

    def upload(self, file_name, src):
        with open(src, 'r', encoding='latin-1') as f:
            message = f.read()
            self.socket.upload(message, file_name, (self.ip, self.port))

        self.close_socket()

    def download(self, name, dst):
        file, _ = self.socket.download(name)

        with open(dst, 'w', encoding='latin-1') as f:
            f.write(file)

        self.close_socket()

    def close_socket(self):
        self.socket.close()