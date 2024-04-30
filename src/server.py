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
        self.port_by_address = {}
    
    def start(self):
        self.protocol.listen()
        self.protocol.socket.setblocking(True)
        i = 0
        while True:
            try:
                print(f"server listening...")
                msg, address = self.protocol.recv()  # recibo un mensaje
                self.protocol.socket.settimeout(1)
                # print(msg)
                
                # si el mensaje es un request de upload, lanzo un thread para manejar
                # el upload. El uploadHandler le manda su puerto al cliente para comunicarse
                if msg.message_type == MessageType.INSTRUCTION and msg.data == "upload":
                    
                    if address in self.port_by_address.keys():
                        pass
                        # print("address se manda un request por segunda vez")
                    # si es la primer conexion de parte del cliente, creo el handler
                    if address not in self.port_by_address.keys():
                        upload_handler = UploadHandler(address, msg.file_name) 
                        self.sessions.append(upload_handler)
                        port = self.sessions[-1].get_port()
                        self.port_by_address[address] = port
                        self.sessions[-1].start()
                    port_msg = Message(MessageType.PORT, 0, str(self.port_by_address[address]), "")
                    # print("mando port_msg")
                    self.protocol.send(port_msg, address)


                # si el request es de download, lo mismo pero con downloadHandler
                elif msg.message_type == MessageType.INSTRUCTION and msg.data == "download":
                    if address in self.port_by_address.keys():
                        pass
                        # print("address se manda un request por segunda vez!")
                    if address not in self.port_by_address.keys():
                        download_handler = DownloadHandler(address, msg.file_name)
                        self.sessions.append(download_handler)
                        port = download_handler.get_port()
                        self.port_by_address[address] = port
                        self.sessions[-1].start()
                    #port_msg = Message(MessageType.PORT, 0, str(self.port_by_address[address]), "")
                    #print("mando port_msg")
                    #self.protocol.send(port_msg, address)
                
                for session in self.sessions: # joineo las sesiones que terminaron
                    if session.ended:
                        session.thread.join()
            except TimeoutError:
                continue
        
        self.protocol.close()

