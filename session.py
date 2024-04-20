from threading import Thread
import queue

class Session:
    def __init__(self, type, send_queue, address):
        self.type = type
        self.send_queue = send_queue
        self.client_adress = address
        self.queue = queue.Queue()

    def start(self):
        sessionThread = Thread(target = self.handle_client, args = (self.type,))
        sessionThread.start()

    def handle_client():
        pass