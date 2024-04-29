from stopandwait import StopAndWaitProtocol
from gbn import GBN
from message import *
from download_handler import *
from upload_handler import *

UPLOAD = 'upload'
DOWNLOAD = 'download'

class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        # self.protocol = StopAndWaitProtocol(ip, port, (ip, port))
        self.protocol = GBN(ip, port, (ip, port))

    def upload(self, file_source, file_name, server_address):
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
        request = Message(MessageType.INSTRUCTION, sequence_number, UPLOAD)
        self.protocol.send_data(request, server_address) # mando un request para hacer upload

        filename_msg = Message(MessageType.FILE_NAME, 0, file_name)
        self.protocol.send_data(filename_msg, server_address)  # mando el nombre del archivo que voy a mandar al nuevo port
        
        with open(file_source, 'r', encoding='latin-1') as f: # mando todo
            data = f.read()
            total = len(data)
            sent_bytes = 0
            
            while sent_bytes < total:
                current_data = data[sent_bytes:sent_bytes + MAX_LENGTH]
                message = Message(MessageType.DATA, sequence_number, current_data)
                self.protocol.send_data(message, server_address)
                sequence_number += 1
                sent_bytes += MAX_LENGTH
        
        end_message = Message(MessageType.END, 0, "")
        self.protocol.send_data(end_message, server_address)
        print("Cliente termino")

    # Manda al server un request para hacer download.
    # Se recibe el puerto del thread downloadHandler
    # Se manda el nombre del archivo al handler a traves del puerto que nos mando
    # Se manda toda la data del archivo
    # Se manda un Message END para indicar que termino el upload
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

        request = Message(MessageType.INSTRUCTION, 0, DOWNLOAD)
        self.protocol.send_data(request, server_address) # Mando un request de download al server

        filename_msg = Message(MessageType.FILE_NAME, 0, file_name)
        self.protocol.send_data(filename_msg, server_address) # Mando el archivo que quiero descargar al nuevo puerto

        self.protocol.client_address = server_address

        next_seq_number = 0
        with open(file_dst, 'w', encoding='latin-1') as f:
            while True:
                try:
                    msg, _ = self.protocol.recv_data() # Recibo data

                    if msg.message_type == MessageType.END:
                        break

                    if msg.sequence_number < next_seq_number: # Por si llego un mensaje repetido
                        continue
                    
                    print(f"Escribiendo [{msg.data}]\n")
                    f.write(msg.data)
                    next_seq_number += 1

                except TimeoutError:
                    self.protocol.socket.settimeout(10)
                    continue
        
        self.protocol.close()
        print("Cliente termino")
