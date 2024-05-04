import os
from message import MessageType, Message
from logger import Logger
from stop_and_wait import StopAndWaitProtocol
from handler_factory import *

class Server:
    def __init__(self, ip, port, args):
        self.storage_dir = args.storage if args.storage[-1] == '/' else args.storage + '/'
        self.ip = ip
        self.port = port
        self.logger = Logger(args.verbose)

        self.sessions = []
        self.port_by_address = {}

        self.protocol = StopAndWaitProtocol(ip, port, self.logger)
        self.number_protocol = args.protocol
        os.makedirs(self.storage_dir, exist_ok=True)

    def start(self):
        """
        Pone a escuchar al servidor únicamente requests de UPLOAD y DOWNLOAD.

        Si recibe un request de UPLOAD, lanza un thread UploadHandler para manejarlo. Este thread
        le envia al cliente su puerto para comunicarse.

        Si recibe un request DOWNLOAD, lanza un thread DownloadHandler para manejarlo. Este thread
        le envia al cliente su puerto para comunicarse.

        Cada cierto tiempo se fija si algún thread termino y en tal caso lo joinea.
        """
        self.protocol.listen()
        self.protocol.socket.setblocking(True)

        while True:
            try:
                msg, address = self.protocol.recv()
                self.protocol.socket.settimeout(1)

                if msg.message_type == MessageType.INSTRUCTION:

                    if address not in self.port_by_address.keys():
                        handler = HandleFactory.create_handle(msg.data, address, self.storage_dir + msg.file_name,
                                                              self.number_protocol, self.logger)
                        self.sessions.append(handler)
                        port = handler.get_port()
                        self.port_by_address[address] = port
                        self.sessions[-1].start()

                    if msg.data == UPLOAD:
                        port_msg = Message(MessageType.PORT, 0, str(self.port_by_address[address]), "")
                        self.protocol.send(port_msg, address)

                for session in self.sessions:
                    if session.ended:
                        session.thread.join()

            except TimeoutError:
                continue

        self.protocol.close()