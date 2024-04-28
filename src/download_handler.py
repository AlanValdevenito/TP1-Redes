from protocol import *
from threading import Thread
from message import *


class DownloadHandler:
    def __init__(self, client_address):
        self.client_address = client_address
        self.thread = Thread(target = self.handle_download)
        self.ended = False

    def start(self):
        self.thread.start()

    def handle_download(self):
        """
        Maneja el request DOWNLOAD.

        Le envia el puerto del nuevo thread al cliente para que el cliente sepa
        a donde comunicarse.

        Se encarga de particionar el archivo y enviar los paquetes.
        """
        self.protocol = StopAndWaitProtocol("127.0.0.1", 0)
        self.protocol.listen()

        port = self.protocol.get_port()
        port_msg = Message(MessageType.PORT, 0, str(port))
        self.protocol.send_data(port_msg, self.client_address) # Le mando mi puerto al cliente
        
        filename_msg, address = self.protocol.recv_data() # Recibo el nombre del archivo a descargar
        if filename_msg.message_type == MessageType.FILE_NAME:   
            filename = filename_msg.data

        # Falta chequear que existe el archivo 'filename'
        with open(filename, 'r', encoding='latin-1') as f: # Abro el archivo y mando la data     
            data = f.read()
            total = len(data)
            sent_bytes = 0
            
            sequence_number = 0
            while sent_bytes < total:
                current_data = data[sent_bytes:sent_bytes + MAX_LENGTH]
                message = Message(MessageType.DATA, sequence_number, current_data)
                self.protocol.send_data(message, self.client_address)
                sequence_number += 1
                sent_bytes += MAX_LENGTH

        end_message = Message(MessageType.END, 0, "")
        self.protocol.send_data(end_message, self.client_address)
        print("Download handler termino")
        self.ended = True