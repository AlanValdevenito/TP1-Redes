from protocol_factory import ProtocolFactory
from threading import Thread
from config import IP, RANDOM_PORT
from gbn import *


class UploadHandler:
    def __init__(self, client_address, filename, protocol, logger):
        self.client_address = client_address
        self.filename = filename
        self.logger = logger

        self.thread = Thread(target=self.handle_upload)
        self.ended = False
        self.protocol = ProtocolFactory.create_protocol(protocol, IP, RANDOM_PORT, logger)
        self.protocol.listen()
        
        self.logger.log(f"UploadHandler: Choose {self.protocol} as protocol.\n")

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
        with open(self.filename, 'wb') as f:
            while True:
                try:
                    msg, _ = self.protocol.recv_data()

                    if msg.message_type == MessageType.END and msg.sequence_number == previous_seq_number + 1:
                        self.protocol.send_end(msg.sequence_number, self.client_address)
                        break

                    if msg.sequence_number == previous_seq_number + 1:
                        f.write(msg.data)
                        previous_seq_number = msg.sequence_number
                        
                        self.logger.log(colored(f"Writing data\n", "green"))

                except TimeoutError:
                    self.protocol.socket.settimeout(10)
                    continue

        self.protocol.close()
        self.ended = True
        self.logger.log("Upload finished.\n")
