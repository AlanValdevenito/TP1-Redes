from protocol_factory import ProtocolFactory
from threading import Thread
from message import Message, MessageType
from config import RANDOM_PORT, MAX_LENGTH


class DownloadHandler:
    def __init__(self, ip, client_address, filename, protocol, logger):
        self.client_address = client_address
        self.filename = filename
        self.logger = logger

        self.thread = Thread(target=self.handle_download)
        self.ended = False
        self.protocol = ProtocolFactory.create_protocol(
            protocol, ip, RANDOM_PORT, logger)
        self.protocol.listen()

        self.logger.log(
            f"DownloadHandler: {self.protocol} was chosen as protocol.\n")

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
        sequence_number = 0
        try:
            
            with open(self.filename, 'rb') as f:
                # Falta comprobar que existe el archivo 'filename'
                data = f.read()
                total = len(data)

                sent_bytes = 0
                
                while sent_bytes < total:
                    current_data = data[sent_bytes:sent_bytes + MAX_LENGTH]
                    message = Message(
                        MessageType.DATA, sequence_number, current_data)

                    self.protocol.send_data(message, self.client_address)

                    sequence_number += 1
                    sent_bytes += MAX_LENGTH
        except FileNotFoundError:
            error_message = Message(MessageType.ERROR, sequence_number, f"No existe el archivo {self.filename}")
            self.protocol.send_data(error_message, self.client_address)
        
        end_message = Message(MessageType.END, sequence_number, "")
        self.protocol.send_data(end_message, self.client_address)
        self.protocol.wait_end(sequence_number, self.client_address)
        self.ended = True
        self.logger.log("Download finished.\n")
