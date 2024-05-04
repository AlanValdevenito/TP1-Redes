from message import *
from protocol import Protocol
from config import MAX_LENGTH

from termcolor import colored


class StopAndWaitProtocol(Protocol):
    def __init__(self, ip, port, logger):
        Protocol.__init__(self, ip, port, logger)

    def send_data(self, message, address):
        """
        Envia un mensaje a la dirección indicada de forma confiable.
        En caso de no recibir un ACK correcto, volverá a enviar el mensaje.
        
        Parámetros:
        - message: Mensaje a enviar.
        - address: Dirección donde se desea enviar el mensaje.
        """

        encoded_msg = message.encode()

        msg_acked = False
        # count = 0
        while not msg_acked:
            try:
                # if count >= 10:
                #     break
                # Puede darse el caso de que el que está mandando el archivo
                # mande un END, el otro conteste con un ACK, pero el ACK se pierde
                # el que mando el ACK se desconecta
                #
                # Cuento cuantos END se perdieron. Si llega a 10
                # es probable que el receiver se haya desconectado
                # en tal caso salgo del send_data
                # if message.message_type == MessageType.END:
                #     count += 1

                self.logger.log(colored(f"Sending {message}\nto {address}\n", "green"))
                self.socket.sendto(encoded_msg, address)

                self.socket.settimeout(0.05)
                msg_acked = self.recv_ack(message.sequence_number)

            except TimeoutError:
                continue

        self.socket.setblocking(True)

    # Private
    def recv_ack(self, seq_number):
        """
        Recibe un ACK.

        Parámetros:
        - seq_number: Número de secuencia del último mensaje enviado.

        Devuelve:
        - True: Si coincide el sequence number del ACK con el número de secuencia del último mensaje enviado.
        - False: Si no coincide el sequence number del ACK con el número de secuencia del último mensaje enviado.
        """

        encoded_msg, _ = self.socket.recvfrom(MAX_LENGTH)
        msg = Message.decode(encoded_msg)

        if msg.sequence_number != seq_number:
            self.logger.log(colored("Llega un ACK. No coincide el numero de secuencia:", "red"))
            self.logger.log(colored(f"Expected = {seq_number}", "red"))
            self.logger.log(colored(f"Got = {msg.sequence_number}\n", "red"))
            return msg.sequence_number == seq_number

        self.logger.log(colored("Llega un ACK. Coincide el numero de secuencia:", "yellow"))
        self.logger.log(colored(f"Expected = {seq_number}", "yellow"))
        self.logger.log(colored(f"Got = {msg.sequence_number}\n", "yellow"))
        return msg.sequence_number == seq_number

    # Private
    def send_ack(self, seq_number, address):
        """
        Envia un ACK.

        Parámetros:
        - seq_number: Número de secuencia del último mensaje recibido.
        - address: Dirección a donde se debe enviar el ACK.
        """

        ack = Message(MessageType.ACK, seq_number, "")
        self.logger.log(colored(f"Se envia el ACK a {address} con el numero de secuencia {seq_number}\n", "yellow"))
        self.socket.sendto(ack.encode(), address)

    def recv_data(self):
        """
        Recibe datos del socket y envia el ACK correspondiente.
        
        Devuelve:
        - Una tupla con una instancia de Message con los datos recibidos y la dirección desde donde fue enviado.
        """

        encoded_msg, address = self.socket.recvfrom(MAX_LENGTH * 2)
        msg = Message.decode(encoded_msg)
        self.logger.log(colored(f"Receiving {msg}\nfrom {address}\n", "green"))

        self.send_ack(msg.sequence_number, address)
        return msg, address
