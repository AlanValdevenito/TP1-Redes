from stopandwait import *
from threading import Thread
from message import *


class DownloadHandler:
    def __init__(self, client_address):
        self.client_address = client_address
        self.thread = Thread(target = self.handle_download)
        self.ended = False
        # self.protocol = GBN(self.client_address[0], 0, client_address)
        self.protocol = StopAndWaitProtocol(self.client_address[0], 0, client_address)

    def start(self):
        self.thread.start()

    def get_port(self):
        return self.protocol.get_port()

    def handle_download(self):
        """
        Maneja el request DOWNLOAD.

        Le envia el puerto del nuevo thread al cliente para que el cliente sepa
        a donde comunicarse.

        Se encarga de particionar el archivo y enviar los paquetes.
        """
        self.protocol.listen()

        instruction, _ = self.protocol.recv_data() # Recibo la instruccion
        print(instruction)
        filename_msg, _ = self.protocol.recv_data() # Recibo el nombre del archivo a descargar
        print(filename_msg)

        if filename_msg.message_type == MessageType.FILE_NAME:   
            filename = filename_msg.data

        sequence_number = 0
        # Falta chequear que existe el archivo 'filename'
        with open(filename, 'r', encoding='latin-1') as f: # Abro el archivo y mando la data     
            data = f.read()
            total = len(data)
            sent_bytes = 0
            
            while sent_bytes < total:
                current_data = data[sent_bytes:sent_bytes + MAX_LENGTH]
                message = Message(MessageType.DATA, sequence_number, current_data)
                self.protocol.send_data(message, self.client_address)
                sequence_number += 1
                sent_bytes += MAX_LENGTH

        end_message = Message(MessageType.END, 0, "")
        self.protocol.send_data(end_message, self.client_address)
        print("Download handler termino\n")
        self.ended = True