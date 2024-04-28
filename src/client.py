from protocol import StopAndWaitProtocol
from message import *
from download_handler import *
from upload_handler import *




class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.protocol = StopAndWaitProtocol(ip, port)

    # Manda al server un request para hacer upload.
    # Se recibe el puerto del thread uploadHandler
    # Se manda el nombre del archivo al handler a traves del puerto que nos mando
    # Se manda toda la data del archivo
    # Se manda un Message END para indicar que termino el upload
    def upload(self, filename, address):
        request = Message(MessageType.INSTRUCTION, 0, "upload")
        server_address = address
        self.protocol.send_data(request, server_address) # mando un request para hacer upload
        msg, address = self.protocol.recv_data()  # recibo el nuevo port
        if msg.message_type == MessageType.PORT:
            new_port = int(msg.data)
            print(f"new_port = {new_port}")
        server_address = ("127.0.0.1", int(new_port))
        filename_msg = Message(MessageType.FILE_NAME, 0, "upload_result.txt")
        self.protocol.send_data(filename_msg, server_address)  # mando el nombre del archivo que voy a mandar al nuevo port
        with open("hola.txt", 'r', encoding='latin-1') as f: # mando todo
            data = f.read()
            total = len(data)
            sent_bytes = 0
            
            sequence_number = 0
            while sent_bytes < total:
                current_data = data[sent_bytes:sent_bytes + MAX_LENGTH]
                print(f"mando data: [{current_data}]")
                message = Message(MessageType.DATA, sequence_number, current_data)
                self.protocol.send_data(message, server_address)
                sequence_number += 1
                sent_bytes += MAX_LENGTH
        end_message = Message(MessageType.END, 0, "")
        self.protocol.send_data(end_message, server_address)
        print("cliente termino")

    # Manda al server un request para hacer download.
    # Se recibe el puerto del thread downloadHandler
    # Se manda el nombre del archivo al handler a traves del puerto que nos mando
    # Se manda toda la data del archivo
    # Se manda un Message END para indicar que termino el upload
    def download(self, filename, address):
        request = Message(MessageType.INSTRUCTION, 0, "download")
        server_address = address
        self.protocol.send_data(request, server_address) # mando un request de download al server
        msg, address = self.protocol.recv_data()         # recibo el puerto del que recibo la data 
        if msg.message_type == MessageType.PORT:
            new_port = int(msg.data)
            print(f"new_port = {new_port}")
        server_address = ("127.0.0.1", int(new_port))
        filename_msg = Message(MessageType.FILE_NAME, 0, "hola.txt")
        self.protocol.send_data(filename_msg, server_address) # mando el archivo que quiero descargar al nuevo puerto
        next_seq_number = 0
        with open("download_result.txt", 'w', encoding='latin-1') as f:
            while True:
                try:
                    msg, address = self.protocol.recv_data() # recibo data
                    msg.print()
                    if msg.message_type == MessageType.END:
                        break
                    if msg.sequence_number < next_seq_number:
                        # por si llego un mensaje repetido
                        continue
                    data = msg.data
                    msg.print()
                    print(f"recibo msg: [{msg.data}]")
                    f.write(data)
                    next_seq_number += 1
                except TimeoutError:
                    self.protocol.socket.settimeout(10)
                    continue
        
        self.protocol.close()

        print("cliente termino")
