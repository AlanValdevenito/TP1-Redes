from protocol_factory import ProtocolFactory
from threading import Thread
from gbn import *

RANDOM_PORT = 0
STOP_AND_WAIT = '1'


class DownloadHandler:
    def __init__(self, client_address, filename, protocol):
        self.client_address = client_address
        self.filename = filename

        self.thread = Thread(target=self.handle_download)
        self.ended = False
        self.protocol = ProtocolFactory.create_protocol(protocol, "127.0.0.1", RANDOM_PORT)
        print(f"DownloadHandler: Se eligio {self.protocol} como protocolo.\n")
        self.protocol.listen()

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

        # Falta comprobar que existe el archivo 'filename'
        with open(self.filename, 'rb') as f:
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

        end_message = Message(MessageType.END, sequence_number, "")
        self.protocol.send_data(end_message, self.client_address)
        self.protocol.wait_end(sequence_number, self.client_address)
        self.ended = True
        print("Download handler termino")
