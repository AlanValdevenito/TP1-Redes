from protocol import StopAndWaitProtocol
from message import *
from download_handler import *
from upload_handler import *
from gbn import *



class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        #self.protocol = StopAndWaitProtocol(ip, port)
        self.protocol = GBN(ip, port)

    # Manda al server un request para hacer upload.
    # Se recibe el puerto del thread uploadHandler
    # Se manda el nombre del archivo al handler a traves del puerto que nos mando
    # Se manda toda la data del archivo
    # Se manda un Message END para indicar que termino el upload
    def upload(self, file_src, filename, address):
        sequence_number = 0
        request = Message(MessageType.INSTRUCTION, sequence_number, "upload", filename)
        print(f"Request: message.data = {request.data}")
        server_address = address
        self.protocol.send(request, server_address) # mando un request para hacer upload
        self.protocol.socket.settimeout(1)
        received_port = False
        while not received_port:
            try:
                msg, address = self.protocol.recv()  # recibo el nuevo port
                if msg.message_type == MessageType.PORT:
                    new_port = int(msg.data)
                    print(f"new_port = {new_port}")
                    received_port = True
                    server_address = ("127.0.0.1", int(new_port))
            except TimeoutError:
                self.protocol.send(request, server_address)
                continue
        sequence_number += 1
        # print("EMPIEZO A MANDAR DATAAAAAaa")
        #filename_msg = Message(MessageType.FILE_NAME, 0, "upload_result.txt")
        #self.protocol.send_data(filename_msg, server_address)  # mando el nombre del archivo que voy a mandar al nuevo port
        with open(file_src, 'r', encoding='latin-1') as f: # mando todo
            data = f.read()
            total = len(data)
            sent_bytes = 0
            # print("antes del while")
            while sent_bytes < total:
                current_data = data[sent_bytes:sent_bytes + MAX_LENGTH]
                # print(f"mando data: [{current_data}]")
                message = Message(MessageType.DATA, sequence_number, current_data)
                print(colored(f"Sending {message}\nto {server_address}\n", "green"))
                self.protocol.send_data(message, server_address)
                sequence_number += 1
                sent_bytes += MAX_LENGTH

        end_message = Message(MessageType.END, sequence_number, "")
        print(colored(f"Sending {end_message}\nto {server_address}\n", "green"))
        self.protocol.send_data(end_message, server_address)
        print("Cliente termino")




    # Manda al server un request para hacer download.
    # Se recibe el puerto del thread downloadHandler
    # Se manda el nombre del archivo al handler a traves del puerto que nos mando
    # Se manda toda la data del archivo
    # Se manda un Message END para indicar que termino el upload
    def download(self, file_dst, filename, address):
        sequence_number = 0
        request = Message(MessageType.INSTRUCTION, sequence_number, "download", filename)
        server_address = address
        # print("mando request download")
        self.protocol.send(request, server_address) # mando un request de download al server
        previous_seq_number = -1
        self.protocol.socket.settimeout(1)
        with open(file_dst, 'w', encoding='latin-1') as f:
            while True:
                try:
                    msg, address = self.protocol.recv_data() # recibo data

                    if msg.message_type == MessageType.END and msg.sequence_number == previous_seq_number + 1:
                        break

                    if msg.sequence_number == previous_seq_number or msg.sequence_number > previous_seq_number + 1:
                        # Mensaje repetido
                        # Mensaje desordenado
                        print(f"Descartamos paquete con numero de secuencia {msg.sequence_number}")
                        continue
                    
                    data = msg.data
                    print(colored(f"Writing data\n", "green"))
                    f.write(data)
                    previous_seq_number = msg.sequence_number
                except TimeoutError:
                    self.protocol.send(request, server_address)
                    continue
        
        self.protocol.close()
        print("Cliente termino")
