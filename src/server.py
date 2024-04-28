from protocol import StopAndWaitProtocol
from message import *
from download_handler import *
from upload_handler import *


# El server unicamente se encarga de escuchar por requests de upload / download
#
# Cuando recibe un nuevo request, tira un thread para manejar el request, y sigue
# escuchando. 
# Cada cierto tiempo se fija si algun thread terminó, y en tal caso lo joinea
class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.protocol = StopAndWaitProtocol(ip, port)
        self.sessions = []

    def start(self):
        self.protocol.listen()
        self.protocol.allow_duplicates()
        self.protocol.socket.setblocking(True)

        while True:
            try:
                print(f"server listening...")
                msg, address = self.protocol.recv_data()  # recibo un mensaje
                self.protocol.socket.settimeout(1)
                msg.print()
                
                # si el mensaje es un request de upload, lanzo un thread para manejar
                # el upload. El uploadHandler le manda su puerto al cliente para comunicarse
                if msg.message_type == MessageType.INSTRUCTION and msg.data == "upload":
                    upload_handler = UploadHandler(address) 
                    self.sessions.append(upload_handler)
                    self.sessions[-1].start()

                # si el request es de download, lo mismo pero con downloadHandler
                elif msg.message_type == MessageType.INSTRUCTION and msg.data == "download":
                    download_handler = DownloadHandler(address)
                    self.sessions.append(download_handler)
                    self.sessions[-1].start()
                
                for session in self.sessions: # joineo las sesiones que terminaron
                    if session.ended:
                        session.thread.join()
            except TimeoutError:
                continue
        
        self.protocol.close()

