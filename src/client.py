from download_handler import *
from upload_handler import *

UPLOAD = 'upload'
DOWNLOAD = 'download'

STOP_AND_WAIT = '1'


class Client:
    def __init__(self, ip, port, protocol):
        self.ip = ip
        self.port = port
        self.protocol = ProtocolFactory.create_protocol(protocol, "127.0.0.1", RANDOM_PORT)
        print(f"Client: Se eligio {self.protocol} como protocolo.\n")

    def upload(self, file_src, file_name, server_address):
        """
        Primero envia al servidor un pedido para hacer upload. Como respuesta a este 
        pedido, recibe un nuevo puerto a donde se comunicara el cliente.

        Luego envia toda la data del archivo 'file_source' y al terminar envia un último
        mensaje para indicar que ha terminado.

        Parámetros:
        - file_source: Nombre del archivo que se desea subir.
        - file_name: Nombre del archivo que se creara y donde se guardara el archivo subido.
        - server_address: Dirección del servidor. Es una tupla (IP, PORT).
        """

        sequence_number = 0
        request = Message(MessageType.INSTRUCTION, sequence_number, UPLOAD, file_name)

        self.protocol.send(request, server_address)  # Mando un request para hacer upload
        self.protocol.socket.settimeout(0.1)

        received_port = False
        while not received_port:
            try:
                msg, address = self.protocol.recv()  # Recibo el nuevo port

                if msg.message_type == MessageType.PORT:
                    new_port = int(msg.data)
                    received_port = True
                    server_address = ("127.0.0.1", int(new_port))

            except TimeoutError:
                self.protocol.send(request, server_address)
                continue

        sequence_number = 0  # ¿Por qué antes estaba inicializado en -1?. Se cambió para que funcione GBN.
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

        end_message = Message(MessageType.END, sequence_number, "")
        self.protocol.send_data(end_message, server_address)
        print("Cliente termino")

    def download(self, file_dst, file_name, server_address):
        """
        Primero envia al servidor un pedido para hacer DOWNLOAD. Como respuesta a este 
        pedido, recibe un nuevo puerto a donde se comunicara el cliente.

        Luego recibe toda la data del archivo 'file_name' y la va escribiendo en el
        archivo 'file_dst'.

        Parámetros:
        - file_dst: Nombre del archivo que se creara y donde se guardara el archivo descargado.
        - file_name: Nombre del archivo que se desea descargar.
        - server_address: Dirección del servidor. Es una tupla (IP, PORT).
        """

        sequence_number = 0
        request = Message(MessageType.INSTRUCTION, sequence_number, DOWNLOAD, file_name)

        self.protocol.send(request, server_address)  # Mando un request de download al server
        self.protocol.socket.settimeout(0.1)

        previous_seq_number = -1
        with open(file_dst, 'wb') as f:
            while True:
                try:
                    msg, address = self.protocol.recv_data()
                    
                    # Si llega un mensaje de tipo END y tiene el número de secuencia esperado (está en orden)...
                    if msg.message_type == MessageType.END and msg.sequence_number == previous_seq_number + 1:
                        break

                    # Si el mensaje tiene el número de secuencia esperado (esta en orden)...
                    if msg.sequence_number == previous_seq_number + 1:
                        f.write(msg.data)
                        print(colored(f"Writing data\n", "green"))

                        previous_seq_number = msg.sequence_number

                    # Si el mensaje está repetido o desordenado...
                    else:
                        # print(f"Descartamos paquete con numero de secuencia {msg.sequence_number}\n")
                        continue

                except TimeoutError:
                    self.protocol.send(request, server_address)
                    continue

        self.protocol.close()
        print("Cliente termino")
