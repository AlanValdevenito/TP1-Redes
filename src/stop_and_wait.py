from socket import *
from message import *
import random

from termcolor import colored

MAX_LENGTH = 64


class StopAndWaitProtocol:
    def __init__(self, ip, port):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.ip = ip
        self.port = port

    def listen(self):
        self.socket.bind((self.ip, self.port))
        print(f"Socket bindeado en {self.socket.getsockname()}")

    def get_port(self):
        return self.socket.getsockname()[1]

    def recv(self):
        encoded_msg, address = self.socket.recvfrom(MAX_LENGTH * 2)
        msg = Message.decode(encoded_msg)
        return msg, address

    def send(self, request, address):
        rdm = random.randint(0, 9)
        if rdm < 8:
            # print(colored(f"Sending {request}\nto {address}\n", "green"))
            self.socket.sendto(request.encode(), address)
        else:
            # print(colored(f"Lost {request}\nto {address}\n", "red"))
            pass

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
                    print(colored(f"Sending {message}\nto {address}\n", "green"))
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
                        print(colored("Se perdio el END", "red"))
                    else:
                        print(colored(f"Lost {message}\nto {address}\n", "red"))

                self.socket.settimeout(0.05)
                msg_acked = self.recv_ack(message.sequence_number)

            except TimeoutError:
                continue

        self.socket.setblocking(True)

    # Private
    def recv_ack(self, seq_number):
        """
        Recibe un ACK.

        Parametros:
        - seq_number: Numero de secuencia del ultimo mensaje enviado.

        Devuelve:
        - True: Si coincide el sequence number del ACK con el numero de secuencia del ultimo mensaje enviado.
        - False: Si no coincide el sequence number del ACK con el numero de secuencia del ultimo mensaje enviado.
        """

        encoded_msg, _ = self.socket.recvfrom(MAX_LENGTH)
        msg = Message.decode(encoded_msg)

        if msg.sequence_number != seq_number:
            print(colored("Llega un ACK. No coincide el numero de secuencia:", "red"))
            print(colored(f"Expected = {seq_number}", "red"))
            print(colored(f"Got = {msg.sequence_number}\n", "red"))
            return msg.sequence_number == seq_number

        print(colored("Llega un ACK. Coincide el numero de secuencia:", "yellow"))
        print(colored(f"Expected = {seq_number}", "yellow"))
        print(colored(f"Got = {msg.sequence_number}\n", "yellow"))
        return msg.sequence_number == seq_number

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
        if rdm < 8:
            print(colored(f"Se envia el ACK a {address} con el numero de secuencia {seq_number}\n", "yellow"))
            self.socket.sendto(ack.encode(), address)
        else:
            print(colored(f"Se perdio el ACK con el numero de secuencia {seq_number}\n", "red"))

    def recv_data(self):
        """
        Recibe datos del socket y envia el ACK correspondiente.
        
        Devuelve:
        - Una tupla con una instancia de Message con los datos recibidos y la direccion desde donde fue enviado.
        """

        encoded_msg, address = self.socket.recvfrom(MAX_LENGTH * 2)
        msg = Message.decode(encoded_msg)
        print(colored(f"Receiving {msg}\nfrom {address}\n", "green"))

        self.send_ack(msg.sequence_number, address)
        return msg, address

    def close(self):
        self.socket.close()
