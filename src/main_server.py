from stopandwait import StopAndWaitProtocol
from message import *
from upload_handler import *
from download_handler import *
from server import *

IP = "127.0.0.1"
PORT = 12000

def main():
    server = Server(IP, PORT)
    server.start()

main()