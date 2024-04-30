from stop_and_wait import StopAndWaitProtocol
from message import *
from download_handler import *
from upload_handler import *

class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

        self.sessions = []
        self.port_by_address = {}

        self.protocol = StopAndWaitProtocol(ip, port)
    
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

        i = 0
        while True:
            try:
                # print(f"Server listening...")
                msg, address = self.protocol.recv()
                self.protocol.socket.settimeout(1)
                
                # Si el mensaje es un request de upload, lanzo un thread para manejar
                # el upload. El uploadHandler le manda su puerto al cliente para comunicarse
                if msg.message_type == MessageType.INSTRUCTION and msg.data == "upload":
                    
                    # Si es la primer conexion de parte del cliente, creo el handler
                    if address not in self.port_by_address.keys():
                        upload_handler = UploadHandler(address, msg.file_name) 
                        self.sessions.append(upload_handler)
                        port = self.sessions[-1].get_port()
                        self.port_by_address[address] = port
                        self.sessions[-1].start()

                    port_msg = Message(MessageType.PORT, 0, str(self.port_by_address[address]), "")
                    self.protocol.send(port_msg, address)

                # Si el request es de download, lo mismo pero con downloadHandler
                elif msg.message_type == MessageType.INSTRUCTION and msg.data == "download":

                    if address not in self.port_by_address.keys():
                        download_handler = DownloadHandler(address, msg.file_name)
                        self.sessions.append(download_handler)
                        port = download_handler.get_port()
                        self.port_by_address[address] = port
                        self.sessions[-1].start()

                    #port_msg = Message(MessageType.PORT, 0, str(self.port_by_address[address]), "")
                    #print("mando port_msg")
                    #self.protocol.send(port_msg, address)
                
                for session in self.sessions: # Join a las sesiones que terminaron
                    if session.ended:
                        session.thread.join()

            except TimeoutError:
                continue
        
        self.protocol.close()

