from socket import *
from message import *
import random

MAX_LENGTH = 64

from termcolor import colored # pa los print

class StopAndWaitProtocol:
    def __init__(self, ip, port):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.ip = ip
        self.port = port

    def listen(self):
        self.socket.bind((self.ip, self.port))
        print(f"Socket bindeado en {(self.ip, self.port)}\n")

    def get_port(self):
        return self.socket.getsockname()[1]
    
    def send_data(self, message, address):
        """
        Envia un mensaje a la direccion indicada de forma confiable.
        En caso de no recibir un ACK correcto, volvera a enviar el mensaje.
        
        Parametros:
        - message: Mensaje a enviar.
        - address: Direccion donde se desea enviar el mensaje.
        """

        encoded_msg = message.encode()
        msg_acked = False
        
        count = 0
        while not msg_acked:
            try:
                if count >= 10:
                    break

                rdm = random.randint(0, 9)
                if rdm < 8:
                    print(colored(f"Sending [{message.data}] to {address}\n", "green"))
                    self.socket.sendto(encoded_msg, address)
                else:
                    # puede darse el caso de que el que esta mandando el archivo
                    # mande un END, el otro conteste con un ACK pero el ACK se pierde
                    # el que mando el ACK se desconecta
                    #
                    # Cuento cuantos END se perdieron. Si llega a 10
                    # es probable que el receiver se haya desconectado
                    # en tal caso salgo del send_data
                    if message.message_type == MessageType.END:
                        count += 1
                        print(colored("Se perdio el END\n", "red"))
                    else:
                        print(colored(f"Se perdio la data [{message.data}]\n", "red"))

                self.socket.settimeout(0.05)
                msg_acked = self.recv_ack(message.sequence_number)
                
            except TimeoutError:
                continue

        self.socket.setblocking(True)

    # Private
    def recv_ack(self, seq_number):
        """
        Recibe un ACK y verifica que el numero de secuencia sea el correcto.

        Parametros:
        - seq_number: Numero de secuencia del ultimo mensaje enviado.

        Devuelve:
        - True: El numero de secuencia es correcto.
        - False: El numero de secuencia no es correcto.
        """

        encoded_msg, _ = self.socket.recvfrom(1024)
        msg = Message.decode(encoded_msg)

        if msg.sequence_number != seq_number:
            print(colored("Llega un ACK. No coincide el numero de secuencia:", "red"))
            print(colored(f"Expected = {seq_number}", "red"))
            print(colored(f"Got = {msg.sequence_number}\n", "red"))

        print(colored("Llega un ACK. Coincide el numero de secuencia:", "green"))
        print(colored(f"Expected = {seq_number}", "green"))
        print(colored(f"Got = {msg.sequence_number}\n", "green"))
        return msg.sequence_number == seq_number
    
    def recv_data(self):
        """
        Recibe datos del socket y envia el ACK correspondiente.
        
        Devuelve:
        - Una tupla con una instancia de Message con los datos recibidos y la direccion desde donde fue enviado.
        """

        encoded_msg, address = self.socket.recvfrom(1024)
        #self.socket.settimeout(0.1)
        msg = Message.decode(encoded_msg)
        self.send_ack(msg.sequence_number, address)
        print(colored(f"Receiving {msg}\nfrom {address}\n", "green"))
        return msg, address
    
    # Private
    def send_ack(self, seq_number, address):
        """
        Envia un ACK.

        Parametros:
        - seq_number: Numero de secuencia del ultimo mensaje recibido.
        - address: Direccion a donde se debe enviar el ACK.
        """

        ack = Message(MessageType.ACK, seq_number, "")

        rdm = random.randint(0, 9)
        if rdm < 5:
            self.socket.sendto(ack.encode(), address)
            print(colored(f"Se envia el ACK con el numero de secuencia {seq_number}\n", "green"))
        else:
            print(colored(f"Se perdio el ACK con el numero de secuencia {seq_number}\n", "red"))
    
    def close(self):
        self.socket.close()