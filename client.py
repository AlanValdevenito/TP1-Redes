from client_protocol import ClientProtocol

class Client:
    def __init__(self, ip, port):
        self.protocol = ClientProtocol(ip, port, 2)
    
    def send(self, message):
        self.protocol.send(message)

    def recv(self):
        return self.protocol.recv()

    def upload(self, file_name, src):
        with open(src, 'r', encoding='latin-1') as f:
            message = f.read()
            self.protocol.upload(message, file_name)

        self.close_socket()

    def download(self, name, dst):
        file = self.protocol.download(name)

        with open(dst, 'w', encoding='latin-1') as f:
            f.write(file)

        self.close_socket()

    def close_socket(self):
        self.protocol.close()