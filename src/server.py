from stopandwait import StopAndWaitProtocol
from gbn import GBN
from message import *
from download_handler import *
from upload_handler import *

MAX_LENGTH = 1024

class Server:
    def __init__(self, ip, port):
        self.sessions = {}

        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.address = (ip,port)
        self.socket.settimeout(1)

    def start(self):
        """
        Pone a escuchar al servidor unicamente requests de UPLOAD y DOWNLOAD.

        Si recibe un request de UPLOAD, lanza un thread UploadHandler para manejarlo. Este thread
        le envia al cliente su puerto para comunicarse.

        Si recibe un request DOWNLOAD, lanza un thread DownloadHandler para manejarlo. Este thread
        le envia al cliente su puerto para comunicarse.

        Cada cierto tiempo se fija si algun thread termino y en tal caso lo joinea.
        """

        self.socket.bind(self.address)  

        while True:
            try:
                # print(f"Server listening...\n")
                encoded_msg, address = self.socket.recvfrom(MAX_LENGTH) # Recibo un mensaje
                msg = Message.decode(encoded_msg)
                
                if msg.message_type == MessageType.INSTRUCTION and msg.data == "upload":
                    print(f"Cliente {address[1]} conectandose")
                    upload_handler = UploadHandler(address) 
                    self.sessions[address] = upload_handler
                    self.sessions[address].start()

                elif msg.message_type == MessageType.INSTRUCTION and msg.data == "download":
                    print(f"Cliente {address[1]} conectandose")
                    download_handler = DownloadHandler(address)
                    self.sessions[address] = download_handler
                    self.sessions[address].start()

                if address in self.sessions and not self.sessions[address].ended:
                    port = self.sessions[address].get_port()
                    # print(port)
                    self.socket.sendto(encoded_msg, (self.address[0], port))

                for address, session in self.sessions.items(): # Join a las sesiones que terminaron
                    if session.ended:
                        session.thread.join()
                        
            except TimeoutError:
                continue
        
        self.protocol.close()

