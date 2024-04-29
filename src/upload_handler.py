from stopandwait import *
from gbn import GBN
from threading import Thread
from message import *


class UploadHandler:
    def __init__(self, client_address):
        self.client_address = client_address
        self.ended = False
        self.thread = Thread(target = self.handle_upload)
        self.protocol = GBN(self.client_address[0], 0, client_address)
        # self.protocol = StopAndWaitProtocol(self.client_address[0], 0, client_address)
        self.protocol.listen()

    def start(self):
        self.thread.start()

    def get_port(self):
        return self.protocol.get_port()

    def handle_upload(self):
        """
        Maneja el request UPLOAD.

        Le envia el puerto del nuevo thread al cliente para que el cliente sepa
        a donde comunicarse.

        Se encarga de recibir los paquetes del archivo y reconstruirlo.
        """
        instruction, _ = self.protocol.recv_data() # Recibo la instruccion
        filename_msg, _ = self.protocol.recv_data() # Recibo el nombre del archivo

        if filename_msg.message_type == MessageType.FILE_NAME:
            filename = filename_msg.data

        next_seq_number = 0
        with open(filename, 'w', encoding='latin-1') as f: # Creo el archivo y recibo la data
            while True:
                try:
                    msg, _ = self.protocol.recv_data()

                    if msg.message_type == MessageType.END:
                        print("llega el END, break")
                        break

                    if msg.sequence_number != next_seq_number or msg.message_type != MessageType.DATA:
                        continue

                    f.write(msg.data)
                    next_seq_number += 1

                except TimeoutError:
                    self.protocol.socket.settimeout(3)
                    continue
        
        print("Upload handler termino\n")
        self.protocol.close()
        self.ended = True