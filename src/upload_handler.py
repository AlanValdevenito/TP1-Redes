from protocol import *
from threading import Thread
from message import *


class UploadHandler:
    def __init__(self, client_address):
        self.client_address = client_address
        self.ended = False
        self.thread = Thread(target = self.handle_upload)

    def start(self):
        self.thread.start()

    def handle_upload(self):
        """
        Maneja el request UPLOAD.

        Le envia el puerto del nuevo thread al cliente para que el cliente sepa
        a donde comunicarse.

        Se encarga de recibir los paquetes del archivo y reconstruirlo.
        """
        self.protocol = StopAndWaitProtocol("127.0.0.1", 0)
        self.protocol.listen()
    
        port = self.protocol.get_port() 
        port_msg = Message(MessageType.PORT, 0, str(port))
        self.protocol.send_data(port_msg, self.client_address) # Le mando mi puerto al cliente

        next_seq_number = 0

        while True:
            filename_msg, _ = self.protocol.recv_data() # Recibo el nombre del archivo

            if filename_msg.message_type == MessageType.FILE_NAME:
                filename = filename_msg.data
                break

        # UnboundLocalError: local variable 'filename' referenced before assignment
        with open(filename, 'w', encoding='latin-1') as f: # Creo el archivo y recibo la data
            while True:
                try:
                    msg, _ = self.protocol.recv_data()

                    if msg.message_type == MessageType.END:
                        break

                    if msg.sequence_number != next_seq_number or msg.message_type != MessageType.DATA:
                        continue

                    f.write(msg.data)
                    next_seq_number += 1

                except TimeoutError:
                    self.protocol.socket.settimeout(10)
                    continue
        
        print("Upload handler termino")
        self.protocol.close()
        self.ended = True