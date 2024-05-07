import time

from .message import Message, MessageType
from .protocol import Protocol
from .config import MAX_LENGTH
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
        while not msg_acked:
            try:
                start_time = time.time()
                self.logger.log(
                    colored(
                        "Sending packet with sequence number"
                        f" {message.sequence_number} to {address}", "green"))
                self.send(message, address)

                self.socket.settimeout(0.05)
                msg_acked = self.recv_ack(message.sequence_number)
                end_time = time.time()
                rtt = end_time - start_time
                self.logger.log_rtt(rtt)

            except TimeoutError:
                continue

        self.socket.setblocking(True)
        return len(encoded_msg)

    def recv_ack(self, seq_number):
        """
        Recibe un ACK.

        Parámetros:
        - seq_number: Número de secuencia del último mensaje enviado.

        Devuelve:
        - True: Si coincide el sequence number del ACK con
                el número de secuencia del último mensaje enviado.
        - False: Si no coincide el sequence number del ACK con
                el número de secuencia del último mensaje enviado.
        """
        encoded_msg, address = self.socket.recvfrom(MAX_LENGTH)
        msg = Message.decode(encoded_msg)

        self.logger.log(colored(f"Receiving ACK from {address}", "yellow"))

        if msg.sequence_number != seq_number:
            self.logger.log(colored(
                f"Sequence number incorrect. Expected ({seq_number})"
                f" != Got ({msg.sequence_number}).\n", "red"))
            return msg.sequence_number == seq_number

        self.logger.log(colored(
            f"Sequence number correct. Expected ({seq_number})"
            f" == Got ({msg.sequence_number}).\n", "yellow"))
        return msg.sequence_number == seq_number

    def send_ack(self, seq_number, address):
        """
        Envia un ACK.

        Parámetros:
        - seq_number: Número de secuencia del último mensaje recibido.
        - address: Dirección a donde se debe enviar el ACK.
        """
        ack = Message(MessageType.ACK, seq_number, "")
        self.logger.log(colored(
            f"Sending ACK to {address} with sequence number"
            f" {seq_number}\n", "yellow"))
        self.send(ack, address)

    def recv_data(self):
        """
        Recibe datos del socket y envia el ACK correspondiente.

        Devuelve:
        - Una tupla con una instancia de Message con los datos
            recibidos y la dirección desde donde fue enviado.
        """
        encoded_msg, address = self.socket.recvfrom(MAX_LENGTH * 2)
        msg = Message.decode(encoded_msg)

        self.logger.log(colored(
            "Receiving packet with sequence number"
            f" {msg.sequence_number} from {address}", "green"))

        self.send_ack(msg.sequence_number, address)
        return msg, address
