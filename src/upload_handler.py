from stop_and_wait import *
from threading import Thread
from message import *
from gbn import *

RANDOM_PORT = 0

class UploadHandler:
    def __init__(self, client_address, filename):
        self.client_address = client_address
        self.filename = filename

        self.thread = Thread(target = self.handle_upload)
        self.ended = False
        
        self.protocol = StopAndWaitProtocol("127.0.0.1", RANDOM_PORT)
        #self.protocol = GBN("127.0.0.1", RANDOM_PORT)
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

        previous_seq_number = -1
        with open(self.filename, 'w', encoding='latin-1') as f:   
            while True:
                try:
                    msg, address = self.protocol.recv_data()

                    if msg.message_type == MessageType.END:
                        break

                    if previous_seq_number == msg.sequence_number or msg.message_type != MessageType.DATA:
                        continue

                    f.write(msg.data)
                    print(colored(f"Writing data\n", "green"))

                    previous_seq_number = msg.sequence_number

                except TimeoutError:
                    self.protocol.socket.settimeout(10)
                    continue
        
        self.protocol.close()
        self.ended = True
        print("Upload handler termino")