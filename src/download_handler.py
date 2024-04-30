from protocol import *
from threading import Thread
from message import *
from gbn import *

class DownloadHandler:
    def __init__(self, client_address, filename):
        self.client_address = client_address
        self.thread = Thread(target = self.handle_download)
        self.ended = False
        self.filename = filename
        # self.protocol = StopAndWaitProtocol("127.0.0.1", 0)
        self.protocol = GBN("127.0.0.1", 0)
        self.protocol.listen()

    def start(self):
        self.thread.start()


    def get_port(self):
        return self.protocol.get_port()
    

    # Maneja la descarga.
    # Le manda el puerto del nuevo thread al cliente para que
    # el cliente sepa a dónde mandarle el filename.
    # 
    # Se encarga de particionar el archivo y mandar los paquetes
    def handle_download(self):
        # falta chequear que existe el archivo 'filename'
        with open(self.filename, 'r', encoding='latin-1') as f:       # abro el archivo y mando la data     
            data = f.read()
            total = len(data)
            sent_bytes = 0
            
            sequence_number = 0
            while sent_bytes < total:
                current_data = data[sent_bytes:sent_bytes + MAX_LENGTH]
                # print(f"mando data: [{current_data}]")
                message = Message(MessageType.DATA, sequence_number, current_data)
                self.protocol.send_data(message, self.client_address)
                sequence_number += 1
                sent_bytes += MAX_LENGTH
                
        # print("mando END message")
        end_message = Message(MessageType.END, sequence_number, "")
        self.protocol.send_data(end_message, self.client_address)
        # print("termine de mandar END emssage")
        print("Download handler termino")
        self.ended = True