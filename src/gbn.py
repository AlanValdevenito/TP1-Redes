from message import Message, MessageType
from protocol import Protocol, EndState
from config import WINDOW_SIZE, MAX_LENGTH
from termcolor import colored
import time


class GBNProtocol(Protocol):
    def __init__(self, ip, port, logger):
        Protocol.__init__(self, ip, port, logger)
        self.n = WINDOW_SIZE
        self.base = 0
        self.signumsec = 0
        self.highest_inorder_seqnum = 0

        self.socket.settimeout(0.0001)
        self.messages = {}
        self.lastackreceived = time.time()

    def recv_data(self):
        encoded_msg, address = self.socket.recvfrom(MAX_LENGTH * 2)
        decoded_msg = Message.decode(encoded_msg)

        if decoded_msg.message_type == MessageType.ACK:
            if decoded_msg.sequence_number < self.base:
                return decoded_msg, address

            self.logger.log(colored(
                "Receiving ACK with sequence number"
                f" {decoded_msg.sequence_number} from {address}.",
                "yellow"))
            self.logger.log(colored("Update base.\n", "yellow"))

            self.base = decoded_msg.sequence_number + 1
            return decoded_msg, address

        if decoded_msg.sequence_number != self.highest_inorder_seqnum:
            print(colored("Wrong order", "red"))
            print(colored(
                "Receiving packet with sequence number"
                f" {decoded_msg.sequence_number} from {address}",
                "red"))
            print(colored("Discard packet", "red"))
            self.send_ack(self.highest_inorder_seqnum, address)
            return decoded_msg, address

        print(colored("Correct order", "green"))
        print(colored(
            "Receiving packet with sequence number"
            f" {decoded_msg.sequence_number} from {address}",
            "green"))
        self.highest_inorder_seqnum += 1
        is_end = decoded_msg.message_type == MessageType.END
        self.send_ack(self.highest_inorder_seqnum, address, is_end)
        return decoded_msg, address

    def send_ack(self, seq_number, address, is_end=False):
        """
        Envia un ACK.

        Parámetros:
        - seq_number: Número de secuencia del último mensaje recibido.
        - address: Dirección a donde se debe enviar el ACK.
        """

        ack = Message(MessageType.ACK, seq_number, "")
        if is_end:
            ack = Message(MessageType.ACK_END, seq_number, "")
            self.end_state = EndState.CLOSE_WAIT
        self.socket.sendto(ack.encode(), address)
        self.logger.log(colored(
            f"Sending ACK to {address} with sequence number"
            f" {seq_number} (next expected package)\n",
            "yellow"))

        """rdm = random.randint(0, 9)
        if rdm < 2:
            self.socket.sendto(ack.encode(), address)
            self.logger.log(colored(
                f"Se envia el ACK a {address} "
                f"con el numero de secuencia {seq_number}\n",
                "yellow"))
        else:
            self.logger.log(colored(
                "Se perdio el ACK con el numero de secuencia"
                f" {seq_number}\n", "red"))"""

    def send_data(self, message, address):
        self.logger.log(
            f"n: {self.n}, base: {self.base}, signumsec: {self.signumsec}")

        self.socket.setblocking(False)
        self.recv_ack(self.base)
        encoded_msg = message.encode()

        if message.message_type == MessageType.END:
            self.logger.log("Receiving END")
            while self.signumsec != self.base:
                self.recv_ack(self.base)
                if time.time() - self.lastackreceived > 1:
                    self.retransmitir_paquetes(address)
            self.logger.log("Finished sending all the packets\n")
            self.end_state = EndState.END_SENT
            self.send_end(message.sequence_number, address)
            return len(encoded_msg)

        if self.signumsec <= self.base + self.n - 1:
            self.logger.log(
                colored(
                    "Sending packet with sequence number"
                    f" {message.sequence_number} to {address}\n",
                    "green"))
            self.socket.sendto(encoded_msg, address)
            self.messages[message.sequence_number] = encoded_msg
            self.signumsec += 1

        else:
            self.logger.log(colored("Full window", "red"))

            message_sent = False
            window_has_room = False
            self.socket.settimeout(0.01)
            while not message_sent:
                try:
                    while not window_has_room:
                        window_has_room = self.recv_ack(self.base)

                    self.logger.log(colored(
                        "Sending packet with sequence number"
                        f" {message.sequence_number} to {address}\n",
                        "green"))
                    self.messages[message.sequence_number] = encoded_msg
                    self.socket.sendto(encoded_msg, address)
                    message_sent = True
                    self.signumsec += 1

                except TimeoutError:
                    self.retransmitir_paquetes(address)

            if message.message_type != MessageType.END:
                return len(encoded_msg)

        self.socket.setblocking(False)
        if time.time() - self.lastackreceived > 0.1:
            self.retransmitir_paquetes(address)

        return len(encoded_msg)

    def recv_ack(self, base):
        """
        Recibe un ACK.

        Parámetros:
        - base: Número de secuencia del paquete no reconocido más antiguo.

        Devuelve:
        - True si el número de secuencia del ACK recibido coincide
        con el número de secuencia base + 1 (próximo paquete esperado).
        - False en caso contrario.
        """
        try:
            encoded_msg, _ = self.socket.recvfrom(MAX_LENGTH * 2)
            msg = Message.decode(encoded_msg)

            self.logger.log(colored(
                "Receiving ACK with sequence number"
                f" {msg.sequence_number} (next expected packet).", "yellow"))

            if msg.sequence_number < base + 1:
                self.logger.log(colored(
                    "Don't update base (repeated ACK).\n", "yellow"))
                return False

            self.logger.log(colored("Update base.\n", "yellow"))
            self.base = msg.sequence_number
            self.lastackreceived = time.time()
            return True

        except BlockingIOError:
            return False

    def retransmitir_paquetes(self, address):
        """
        Retransmite los paquetes que ya han sido enviados,
        pero todavía no se han reconocido. Esto es el
        intervalo [base, signumsec-1].
        """
        self.lastackreceived = time.time()

        print(colored("Timeout", "blue"))
        self.logger.log(
            colored("-------------------------------------", "blue"))
        self.logger.log(
            colored("Re-sending packets with sequence number"
                    f" [{self.base}, {self.signumsec - 1}]\n", "blue"))
        for i in range(self.base, self.signumsec):
            if i in self.messages:
                print(colored(
                    "Re-sending packet with sequence number"
                    f" {i} to {address}", "blue"))
                self.socket.sendto(self.messages[i], address)
        self.logger.log(colored(
            "-------------------------------------\n", "blue"))
