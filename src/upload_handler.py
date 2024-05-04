from protocol_factory import ProtocolFactory
from threading import Thread
from gbn import *

RANDOM_PORT = 0


class UploadHandler:
    def __init__(self, client_address, filename, protocol, logger):
        self.client_address = client_address
        self.filename = filename
        self.logger = logger

        self.thread = Thread(target=self.handle_upload)
        self.ended = False
        self.protocol = ProtocolFactory.create_protocol(protocol, "127.0.0.1", RANDOM_PORT, logger)
        self.logger.log(f"UploadHandler: Se eligio {self.protocol} como protocolo.\n")
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
        with open(self.filename, 'wb') as f:
            while True:
                try:
                    msg, address = self.protocol.recv_data()

                    # Si llega un mensaje de tipo END y tiene el número de secuencia esperado (esta en orden)...
                    if msg.message_type == MessageType.END and msg.sequence_number == previous_seq_number + 1:
                        self.protocol.send_end(msg.sequence_number, self.client_address)
                        break

                    # Si el mensaje tiene el número de secuencia esperado (esta en orden)...
                    if msg.sequence_number == previous_seq_number + 1:
                        f.write(msg.data)
                        self.logger.log(colored(f"Writing data\n", "green"))

                        previous_seq_number = msg.sequence_number

                    # Si el mensaje está repetido o desordenado...
                    else:
                        # print(colored(f"Descartamos paquete con numero de secuencia {msg.sequence_number}\n", "red"))
                        pass

                except TimeoutError:
                    self.protocol.socket.settimeout(10)
                    continue

        self.protocol.close()
        self.ended = True
        self.logger.log("Upload handler termino")
