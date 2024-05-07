from logger import Logger
from protocol_factory import ProtocolFactory
from message import Message, MessageType
from config import UPLOAD, DOWNLOAD, IP, RANDOM_PORT, MAX_LENGTH
from termcolor import colored
import os


class Client:
    def __init__(self, ip, port, args):
        self.ip = ip
        self.port = port
        self.logger = Logger(args.verbose)
        self.protocol = ProtocolFactory.create_protocol(
            args.protocol, IP, RANDOM_PORT, self.logger)

        self.logger.log(f"Client: {self.protocol} was chosen as protocol.\n")

    def upload(self, file_src, file_name, server_address):
        """
        Primero envia al servidor un pedido para hacer upload.
        Como respuesta a este pedido, recibe un nuevo puerto
        a donde se comunicara el cliente.

        Luego envia toda la data del archivo 'file_source'
        y al terminar envia un último mensaje para indicar
        que ha terminado.

        Parámetros:
        - file_source: Nombre del archivo que se desea subir.
        - file_name: Nombre del archivo que se creara y donde
                    se guardara el archivo subido.
        - server_address: Dirección del servidor. Es una tupla (IP, PORT).
        """

        if not os.path.isfile(file_src):
            self.logger.log(colored(f"Error: {file_src} does not exist", "red"), True)
            return

        sequence_number = 0
        request = Message(
            MessageType.INSTRUCTION, sequence_number, UPLOAD, file_name)
        self.protocol.send(request, server_address)
        self.protocol.socket.settimeout(0.1)

        received_port = False
        while not received_port:
            try:
                msg, address = self.protocol.recv()

                if msg.message_type == MessageType.PORT:
                    new_port = int(msg.data)
                    received_port = True
                    server_address = (self.ip, int(new_port))

            except TimeoutError:
                self.protocol.send(request, server_address)
                continue

        sequence_number = 0
        with open(file_src, 'rb') as f:
            data = f.read()
            total = len(data)

            sent_bytes = 0
            while sent_bytes < total:
                current_data = data[sent_bytes:sent_bytes + MAX_LENGTH]
                message = Message(MessageType.DATA, sequence_number, current_data)

                self.protocol.send_data(message, server_address)

                sequence_number += 1
                sent_bytes += MAX_LENGTH

        self.logger.log("Sending END\n")
        end_message = Message(MessageType.END, sequence_number, "")
        self.protocol.send_data(end_message, server_address)
        self.protocol.wait_end(sequence_number, server_address)
        self.logger.log("Client finished")

    def download(self, file_dst, file_name, server_address):
        """
        Primero envia al servidor un pedido para hacer DOWNLOAD.
        Como respuesta a este pedido, recibe un nuevo puerto
        a donde se comunicara el cliente.

        Luego recibe toda la data del archivo 'file_name'
        y la va escribiendo en el archivo 'file_dst'.

        Parámetros:
        - file_dst: Nombre del archivo que se creara y donde
                    se guardara el archivo descargado.
        - file_name: Nombre del archivo que se desea descargar.
        - server_address: Dirección del servidor. Es una tupla (IP, PORT).
        """
        sequence_number = 0
        request = Message(
            MessageType.INSTRUCTION, sequence_number, DOWNLOAD, file_name)

        self.protocol.send(request, server_address)
        self.protocol.socket.settimeout(0.1)

        previous_seq_number = -1
        with open(file_dst, 'wb') as f:
            while True:
                try:
                    msg, address = self.protocol.recv_data()

                    if (msg.message_type == MessageType.END and
                            msg.sequence_number == previous_seq_number + 1):
                        self.protocol.send_end(msg.sequence_number, address)
                        break
                    
                    if msg.message_type == MessageType.ERROR:
                        self.logger.log(colored(f"Error: {msg.data}", "red"), True)
                        continue

                    if msg.sequence_number == previous_seq_number + 1:
                        f.write(msg.data)
                        previous_seq_number = msg.sequence_number

                        self.logger.log(colored("Writing data\n", "green"))

                except TimeoutError:
                    self.protocol.send(request, server_address)
                    continue

        self.protocol.close()
        self.logger.log("Client finished")
