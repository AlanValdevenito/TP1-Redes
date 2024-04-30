from stop_and_wait import StopAndWaitProtocol
from message import *
from download_handler import *
from upload_handler import *
from gbn import *

UPLOAD = 'upload'
DOWNLOAD = 'download'

class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

        self.protocol = StopAndWaitProtocol(ip, port)
        # self.protocol = GBN(ip, port)

    def upload(self, file_src, file_name, server_address):
        """
        Primero envia al servidor un pedido para hacer upload. Como respuesta a este 
        pedido, recibe un nuevo puerto a donde se comunicara el cliente.

        Luego envia toda la data del archivo 'file_source' y al terminar envia un ultimo
        mensaje para indicar que ha terminado.

        Parametros:
        - file_source: Nombre del archivo que se desea subir.
        - file_name: Nombre del archivo que se creara y donde se guardara el archivo subido.
        - server_address: Direccion del servidor. Es una tupla (IP, PORT).
        """

        sequence_number = 0
        request = Message(MessageType.INSTRUCTION, sequence_number, UPLOAD, file_name)

        self.protocol.send(request, server_address) # Mando un request para hacer upload
        self.protocol.socket.settimeout(1)

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

        sequence_number += 1
        with open(file_src, 'r', encoding='latin-1') as f:
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

        Parametros:
        - file_dst: Nombre del archivo que se creara y donde se guardara el archivo descargado.
        - file_name: Nombre del archivo que se desea descargar.
        - server_address: Direccion del servidor. Es una tupla (IP, PORT).
        """

        sequence_number = 0
        request = Message(MessageType.INSTRUCTION, sequence_number, DOWNLOAD, file_name)

        self.protocol.send(request, server_address) # Mando un request de download al server
        self.protocol.socket.settimeout(1)

        previous_seq_number = -1
        with open(file_dst, 'w', encoding='latin-1') as f:
            while True:
                try:
                    msg, address = self.protocol.recv_data()

                    # Si llega un mensaje de tipo END y esta en orden...
                    if msg.message_type == MessageType.END and msg.sequence_number == previous_seq_number + 1:
                        break

                    # Si el mensaje esta repetido o desordenado...
                    if msg.sequence_number == previous_seq_number or msg.sequence_number > previous_seq_number + 1:
                        print(f"Descartamos paquete con numero de secuencia {msg.sequence_number}\n")
                        continue
                    
                    f.write(msg.data)
                    print(colored(f"Writing data\n", "green"))
                    
                    previous_seq_number = msg.sequence_number

                except TimeoutError:
                    self.protocol.send(request, server_address)
                    continue
        
        self.protocol.close()
        print("Cliente termino")
