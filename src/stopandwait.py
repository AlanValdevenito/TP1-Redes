from socket import *
from message import *
import random

MAX_LENGTH = 32

from termcolor import colored # pa los print

class StopAndWaitProtocol:
    def __init__(self, ip, port, client_address):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.ip = ip
        self.port = port
        self.previous_sequence_number = -1
        self.last_message_address = None
        self.allows_duplicates = False

        self.client_address = client_address

    def listen(self):
        self.socket.bind((self.ip, self.port))
        print(f"Socket bindeado en {self.socket.getsockname()}\n")

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
        end_count = 0
        count = 0
        while not msg_acked:
            try:
                if end_count >= 10 or count == 10:
                    # puedo tirar un error de conexion o algo asi
                    break

                """print(colored(f"Sending {message}\nto {address}\n", "green"))
                self.socket.sendto(encoded_msg, address)"""

                rdm = random.randint(0, 9)
                if rdm < 5:
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
                        end_count += 1
                        print(colored("Se perdio el END\n", "red"))
                    else:
                        print(colored(f"Lost {message}\nto {address}\n", "red"))

                self.socket.settimeout(1)
                print(colored(f"Esperando ACK de {self.client_address}\n", "yellow"))
                msg_acked = self.recv_ack(message.sequence_number)

            except TimeoutError:
                continue
            count += 1
            
        self.socket.setblocking(True)

    # Private
    def recv_ack(self, seq_number):
        encoded_msg, address = self.socket.recvfrom(MAX_LENGTH)
        msg = Message.decode(encoded_msg)

        if msg.sequence_number != seq_number:
            print(colored("Llega un ACK. No coincide el numero de secuencia:", "red"))
            print(colored(f"Expected = {seq_number}", "red"))
            print(colored(f"Got = {msg.sequence_number}\n", "red"))

        print(colored("Llega un ACK. Coincide el numero de secuencia:", "yellow"))
        print(colored(f"Expected = {seq_number}", "yellow"))
        print(colored(f"Got = {msg.sequence_number}\n", "yellow"))
        return msg.sequence_number == seq_number
    
    def recv_data(self):
        """
        Recibe datos del socket y envia el ACK correspondiente.
        
        Devuelve:
        - Una tupla con una instancia de Message con los datos recibidos y la direccion desde donde fue enviado.
        """

        encoded_msg, _ = self.socket.recvfrom(MAX_LENGTH*2) # Si no multiplicamos MAX_LENGTH no se recibe toda la data
        msg = Message.decode(encoded_msg)

        self.send_ack(msg.sequence_number, self.client_address)
        print(colored(f"Receiving {msg}\nfrom {self.client_address}\n", "green"))
        return msg, self.client_address
    
    # Private
    def send_ack(self, seq_number, address):
        """
        Envia un ACK.

        Parametros:
        - seq_number: Numero de secuencia del ultimo mensaje recibido.
        - address: Direccion a donde se debe enviar el ACK.
        """

        ack = Message(MessageType.ACK, seq_number, "")
        """self.socket.sendto(ack.encode(), address)
        print(colored(f"Se envia el ACK a {address} con el numero de secuencia {seq_number}\n", "yellow"))"""

        rdm = random.randint(0, 9)
        if rdm < 5:
            self.socket.sendto(ack.encode(), address)
            print(colored(f"Se envia el ACK a {address} con el numero de secuencia {seq_number}\n", "yellow"))
        else:
            print(colored(f"Se perdio el ACK con el numero de secuencia {seq_number}\n", "red"))
    
    def close(self):
        self.socket.close()