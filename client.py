from client_protocol import ClientProtocol

class Client:
    def __init__(self, ip, port):
        self.protocol = ClientProtocol(ip, port, 0.5)
    
    def send(self, message):
        self.protocol.send(message)

    def recv(self):
        return self.protocol.recv()

    def upload(self, file_name, src):
        print("Client.upload (1): Abriendo el archivo\n")

        with open(src, 'r', encoding='latin-1') as f:
            message = f.read()
            print("Client.upload (2): Leyendo el archivo e invocando el metodo 'upload' del protocolo\n")
            self.protocol.upload(message, file_name)

        print("Client.upload (6): Terminamos")
        self.close_socket()

    def download(self, name, dst):
        file = self.protocol.download(name)

        print("Client.download: Guardando el archivo\n")
        with open(dst, 'w', encoding='latin-1') as f:
            f.write(file)

        print("Client.download: Terminamos")
        self.close_socket()

    def close_socket(self):
        self.protocol.close()