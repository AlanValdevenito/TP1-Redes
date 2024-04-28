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

    # Maneja el upload
    # Le manda el puerto del nuevo thread al cliente para que
    # el cliente sepa a dónde mandarle el filename y la data
    # 
    # Se encarga de recibir los paquetes del archivo y reconstruirlo
    def handle_upload(self):
        self.protocol = StopAndWaitProtocol("127.0.0.1", 0)
        self.protocol.listen()
        port = self.protocol.get_port() 
        port_msg = Message(MessageType.PORT, 0, str(port))
        print(f"uploadHandler: mando nuevo port = {port}")
        self.protocol.send_data(port_msg, self.client_address) # le mando mi puerto al cliente
        next_seq_number = 0
        filename_msg, address = self.protocol.recv_data()       # recibo el nombre del archivo
        if filename_msg.message_type == MessageType.FILE_NAME:
            filename = filename_msg.data
        with open(filename, 'w', encoding='latin-1') as f:      # creo el archivo y recibo la data
            while True:
                try:
                    msg, address = self.protocol.recv_data()
                    msg.print()
                    if msg.message_type == MessageType.END:
                        break
                    if msg.message_type != MessageType.DATA:
                        continue
                    #if msg.sequence_number != next_seq_number:
                    #    continue
                    data = msg.data
                    msg.print()
                    print(f"recibo msg: [{msg.data}]")
                    f.write(data)
                    next_seq_number += 1
                except TimeoutError:
                    self.protocol.socket.settimeout(10)
                    continue
        
        self.protocol.close()
        print("upload handler termino")
        self.ended = True