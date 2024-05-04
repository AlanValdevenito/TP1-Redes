from message import Message, MessageType
from protocol import Protocol
from config import MAX_LENGTH
from termcolor import colored
import time

WINDOW_SIZE = 10


class GBNProtocol(Protocol):
    def __init__(self, ip, port, logger):
        Protocol.__init__(self, ip, port, logger)
        self.n = WINDOW_SIZE
        self.base = 0  # Número de secuencia del paquete no reconocido más antiguo.
        self.signumsec = 0  # Número de secuencia del siguiente paquete que se va a enviar.
        self.highest_inorder_seqnum = 0  # Número de secuencia en orden y ya reconocido más alto.

        self.socket.settimeout(0.0001)
        self.messages = {}
        self.lastackreceived = time.time()

    def recv_data(self):
        encoded_msg, address = self.socket.recvfrom(MAX_LENGTH * 2)
        decoded_msg = Message.decode(encoded_msg)
        self.logger.log(colored(f"Receiving {decoded_msg}\nfrom {address}\n", "green"))

        if decoded_msg.message_type == MessageType.ACK:
            if decoded_msg.sequence_number < self.base:
                return decoded_msg, address

            self.logger.log(
                f"Llega un ACK con numero de secuencia {decoded_msg.sequence_number}. Aumentamos la base.\n")
            self.base = decoded_msg.sequence_number + 1
            # if self.base == self.signumsec:
            # detener timer
            # else:
            # self.lastackreceived = time.time()
            return decoded_msg, address

        # Si el número de secuencia recibido no sigue el orden, descartamos el paquete y
        # reenviamos el último ACK recibido. Por ejemplo:
        # 1) Recibimos el pkt0: sequence_number = 0, highest_inorder_seqnum = 0 → 1.
        # 2) Recibimos el pkt1: sequence_number = 1, highest_inorder_seqnum = 1 → 2.
        # 3) Se pierde el pkt2.
        # 4) Recibimos el pkt3: sequence_number = 3, highest_inorder_seqnum = 2.
        # Se descarta el pkt3 y enviamos ACK con número de secuencia 2 (próximo paquete esperado).
        if decoded_msg.sequence_number != self.highest_inorder_seqnum:
            self.logger.log(
                f"No se sigue el orden, descartamos el paquete y reenviamos el ACK con numero de secuencia {self.highest_inorder_seqnum}\n")
            self.send_ack(self.highest_inorder_seqnum, address)
            return decoded_msg, address  # Se descarta el paquete en client.py

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
        self.socket.sendto(ack.encode(), address)
        self.logger.log(
            colored(f"Se envia el ACK a {address} con el numero de secuencia {seq_number} (proximo paquete esperado)\n",
                    "yellow"))

        """rdm = random.randint(0, 9)
        if rdm < 2:
            self.socket.sendto(ack.encode(), address)
            self.logger.log(colored(f"Se envia el ACK a {address} con el numero de secuencia {seq_number}\n", "yellow"))
        else:
            self.logger.log(colored(f"Se perdio el ACK con el numero de secuencia {seq_number}\n", "red"))"""

    def send_data(self, message, address):
        self.logger.log(f"n: {self.n}, base: {self.base}, signumsec: {self.signumsec}\n")

        encoded_msg = message.encode()
        # Intentamos recibir un ACK de forma no bloqueante que nos permita mover la ventana.
        self.socket.setblocking(False)
        self.recv_ack(self.base)

        if self.signumsec <= self.base + self.n - 1:
            self.logger.log(colored(f"Sending packet {self.signumsec} {message}\nto {address}\n", "green"))
            self.socket.sendto(encoded_msg, address)
            self.messages[message.sequence_number] = encoded_msg
            """rdm = random.randint(0, 9)
            if rdm < 2:
                self.logger.log(colored(f"Sending {message}\nto {address}\n", "green"))
                self.socket.sendto(encoded_msg, address)
            else:
                self.logger.log(colored(f"Lost {message}\nto {address}\n", "red"))"""

            self.signumsec += 1

        else:
            self.logger.log(colored("Ventana llena", "red"))
            """print(colored(f"Lost {message}\nto {address}\n", "red"))
            self.socket.setblocking(True)

            # Esperamos por un ACK de forma bloqueante que nos permita mover la ventana.
            # Cuando llega el ACK reenviamos el paquete que quedo fuera de la ventana.
            if self.recv_ack(self.base):
                print(colored(f"Sending {message}\nto {address}\n", "green"))
                self.socket.sendto(encoded_msg, address)
                self.messages[self.signumsec] = encoded_msg
                self.signumsec += 1
            else:"""
            # Se recibió un ACK repetido. Por ejemplo: inicialmente, base = 0, signumsec = 1.
            # 1) Enviamos el pkt0.
            # 2) Enviamos el pkt1.
            # 3) Recibimos ack0 con número de secuencia 1 (próximo pkt esperado). Actualizamos base = 1.
            # 4) Ocurre un timeout prematuro debido al pkt 1. Reenviamos el pkt 1.
            # 5) Recibimos ack0 con número de secuencia 1 (próximo pkt esperado).

            # Luego, no actualizamos la base, ya que es un acknowledge repetido.
            """
            is_in_order = False
            while time.time() - self.lastackreceived < 0.1:
                is_in_order = self.recv_ack(self.base)
                
            if not is_in_order:
                self.retransmitir_paquetes(address)
            """
            message_sent = False
            window_has_room = False
            self.socket.settimeout(0.01)
            while not message_sent:
                try:
                    # espero hasta que haya espacio en la ventana
                    while not window_has_room:
                        window_has_room = self.recv_ack(self.base)

                    # hay espacio en la ventana => mando el mensaje
                    self.logger.log(colored(f"Sending {message}\nto {address}\n", "green"))
                    self.messages[message.sequence_number] = encoded_msg
                    self.socket.sendto(encoded_msg, address)
                    message_sent = True
                    self.signumsec += 1

                # si no me llegan acks, retransmito
                except TimeoutError:
                    self.retransmitir_paquetes(address)

            # si el mensaje que queria enviar no es END, salgo
            if message.message_type != MessageType.END:
                return
            # Puede pasar que la diferencia no sea mayor a 0.0001 y al final no se envíen
            # todos los paquetes, incluyendo el de tipo END.
            # Esto como consecuencia deja bloqueado al cliente.

        # Si aumentamos 0.0001 a 0.000001 ya no tenemos este problema.
        self.socket.setblocking(False)
        self.logger.log(f"Timeout: {time.time()} - {self.lastackreceived} = {time.time() - self.lastackreceived}\n")
        if time.time() - self.lastackreceived > 0.1:
            self.retransmitir_paquetes(address)

        if message.message_type == MessageType.END:
            self.logger.log("Llega END, mandamos todos")
            while self.signumsec != self.base:
                self.recv_ack(self.base)
                if time.time() - self.lastackreceived > 0.1:
                    self.retransmitir_paquetes(address)
            self.logger.log("Terminamos de mandar todos los paquetes")

    def recv_ack(self, base):
        """
        Recibe un ACK.

        Parámetros:
        - base: Número de secuencia del paquete no reconocido más antiguo.

        Devuelve:
        - True si el número de secuencia del ACK recibido coincide con el número de secuencia
        base + 1 (próximo paquete esperado).
        - False en caso contrario.
        """
        try:
            encoded_msg, _ = self.socket.recvfrom(MAX_LENGTH * 2)
            msg = Message.decode(encoded_msg)

            self.logger.log(
                colored(f"Llega un ACK con numero de secuencia {msg.sequence_number} (proximo paquete esperado).",
                        "yellow"))

            if msg.sequence_number < base + 1:
                self.logger.log(colored(f"No actualizamos la base (llego un ACK repetido).\n", "yellow"))
                return False

            self.logger.log(colored(f"Actualizamos la base.\n", "yellow"))
            self.base = msg.sequence_number
            self.lastackreceived = time.time()  # Reiniciamos el timer cuando llega un ACK
            return True

        except BlockingIOError:
            return False

    def retransmitir_paquetes(self, address):
        """
        Retransmite los paquetes que ya han sido enviados, pero todavía no se han reconocido. Esto es
        el intervalo [base, signumsec-1].
        """
        self.logger.log(colored("-------------------------------------", "blue"))
        self.lastackreceived = time.time()
        self.logger.log(
            colored(f"Reenviando paquetes con numero de secuencia [{self.base}, {self.signumsec - 1}]\n", "blue"))
        for i in range(self.base, self.signumsec):
            if i in self.messages:
                self.logger.log(
                    colored(f"Re-sending packet {i} {Message.decode(self.messages[i])}\nto {address}\n", "blue"))
                self.socket.sendto(self.messages[i], address)
        self.logger.log(colored("-------------------------------------\n", "blue"))
