from protocol import StopAndWaitProtocol
from message import *
from download_handler import *
from upload_handler import *

class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.protocol = StopAndWaitProtocol(ip, port)
        self.sessions = []

    def start(self):
        """
        Pone a escuchar al servidor unicamente requests de UPLOAD y DOWNLOAD.

        Si recibe un request de UPLOAD, lanza un thread UploadHandler para manejarlo. Este thread
        le envia al cliente su puerto para comunicarse.

        Si recibe un request DOWNLOAD, lanza un thread DownloadHandler para manejarlo. Este thread
        le envia al cliente su puerto para comunicarse.

        Cada cierto tiempo se fija si algun thread termino y en tal caso lo joinea.
        """
        self.protocol.listen()
        self.protocol.socket.setblocking(True)

        while True:
            try:
                print(f"Server listening...\n")
                msg, address = self.protocol.recv_data() # Recibo un mensaje
                self.protocol.socket.settimeout(1)
                
                if msg.message_type == MessageType.INSTRUCTION and msg.data == "upload":
                    upload_handler = UploadHandler(address) 
                    self.sessions.append(upload_handler)
                    self.sessions[-1].start()

                elif msg.message_type == MessageType.INSTRUCTION and msg.data == "download":
                    download_handler = DownloadHandler(address)
                    self.sessions.append(download_handler)
                    self.sessions[-1].start()
                
                for session in self.sessions: # Join a las sesiones que terminaron
                    if session.ended:
                        session.thread.join()
                        
            except TimeoutError:
                continue
        
        self.protocol.close()

