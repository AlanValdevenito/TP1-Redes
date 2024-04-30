from protocol import *
from threading import Thread
from message import *
from gbn import *


class UploadHandler:
    def __init__(self, client_address, filename):
        self.client_address = client_address
        self.ended = False
        self.thread = Thread(target = self.handle_upload)
        self.filename = filename
        self.protocol = StopAndWaitProtocol("127.0.0.1", 0)
        #self.protocol = GBN("127.0.0.1", 0)
        self.protocol.listen()

    def start(self):
        self.thread.start()

    def get_port(self):
        return self.protocol.get_port()
    
    # Maneja el upload
    # Le manda el puerto del nuevo thread al cliente para que
    # el cliente sepa a dónde mandarle el filename y la data
    # 
    # Se encarga de recibir los paquetes del archivo y reconstruirlo
    def handle_upload(self):
        """
        port = self.protocol.get_port() 
        port_msg = Message(MessageType.PORT, 0, str(port))
        print(f"uploadHandler: mando nuevo port = {port}")
        self.protocol.send_data(port_msg, self.client_address) # le mando mi puerto al cliente
        
        filename_msg, address = self.protocol.recv_data()       # recibo el nombre del archivo
        if filename_msg.message_type == MessageType.FILE_NAME:
            filename = filename_msg.data
        """
        previous_seq_number = -1
        with open(self.filename, 'w', encoding='latin-1') as f:      # creo el archivo y recibo la data
            while True:
                try:
                    msg, address = self.protocol.recv_data()
                    msg.print()
                    if msg.message_type == MessageType.END:
                        break
                    if previous_seq_number == msg.sequence_number or msg.message_type != MessageType.DATA:
                        continue
                    data = msg.data
                    msg.print()
                    print(f"recibo msg: [{msg.data}]")
                    f.write(data)
                    previous_seq_number = msg.sequence_number
                except TimeoutError:
                    self.protocol.socket.settimeout(10)
                    continue
        
        self.protocol.close()
        print("upload handler termino")
        self.ended = True