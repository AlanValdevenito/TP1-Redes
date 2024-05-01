from socket import *
from message import Message, MessageType
from termcolor import colored 
import random
import time

WINDOW_SIZE = 10
MAX_LENGTH = 64

class GBN:
    def __init__(self, ip, port):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.ip = ip
        self.port = port

        self.n = WINDOW_SIZE
        self.base = 0 # Numero de secuencia del paquete no reconocido mas antiguo.
        self.signumsec = 0 # Numero de secuencia del siguiente paquete que se va a enviar.
        self.highest_inorder_seqnum = 0 # Numero de secuencia en orden y ya reconocido mas alto.

        self.socket.settimeout(0.0001)
        self.messages = {}
        self.lastackreceived = time.time()

    def recv(self):
        encoded_msg, address = self.socket.recvfrom(MAX_LENGTH * 2)
        decoded_msg = Message.decode(encoded_msg)
        # print(colored(f"Receiving {decoded_msg}\nfrom {address}\n", "green"))
        return decoded_msg, address

    def send(self, request, address):
        self.socket.sendto(request.encode(), address)
        # print(colored(f"Sending {request}\nto {address}\n", "green"))  

    def listen(self):
        self.socket.bind((self.ip, self.port))
        print(f"Socket bindeado en {self.socket.getsockname()}\n")

    def get_port(self):
        return self.socket.getsockname()[1]

    def recv_data(self):
        encoded_msg, address = self.socket.recvfrom(MAX_LENGTH*2)
        decoded_msg = Message.decode(encoded_msg)
        print(colored(f"Receiving {decoded_msg}\nfrom {address}\n", "green"))

        if decoded_msg.message_type == MessageType.ACK:
            if decoded_msg.sequence_number < self.base:
                return decoded_msg, address
            
            print(f"Llega un ACK con numero de secuencia {decoded_msg.sequence_number}. Aumentamos la base.\n")
            self.base = decoded_msg.sequence_number + 1
            #if self.base == self.signumsec:
                # detener timer
            #else:
                # resetear timer
            return decoded_msg, address
        
        # Si el numero de secuencia recibido no sigue el orden, descartamos el paquete y reenviamos el ultimo ACK recibido. Por ejemplo:
        # 1) Recibimos el pkt0: sequence_number = 0, highest_inorder_seqnum = 0 -> 1.
        # 2) Recibimos el pkt1: sequence_number = 1, highest_inorder_seqnum = 1 -> 2.
        # 3) Se pierde el pkt2.
        # 4) Recibimos el pkt3: sequence_number = 3, highest_inorder_seqnum = 2. Se descarta el pkt3 y enviamos ACK con numero 
        # de secuencia 2 (proximo paquete esperado).
        if decoded_msg.sequence_number != self.highest_inorder_seqnum:
            print(f"No se sigue el orden, descartamos el paquete y reenviamos el ACK con numero de secuencia {self.highest_inorder_seqnum}\n")
            self.send_ack(self.highest_inorder_seqnum, address)
            return decoded_msg, address # Se descarta el paquete en client.py

        self.highest_inorder_seqnum += 1
        self.send_ack(self.highest_inorder_seqnum, address)
        return decoded_msg, address
        
    def send_ack(self, seq_number, address):
        """
        Envia un ACK.

        Parametros:
        - seq_number: Numero de secuencia del ultimo mensaje recibido.
        - address: Direccion a donde se debe enviar el ACK.
        """

        ack = Message(MessageType.ACK, seq_number, "")
        # self.socket.sendto(ack.encode(), address)
        # print(colored(f"Se envia el ACK a {address} con el numero de secuencia {seq_number} (proximo paquete esperado)\n", "yellow"))
        
        rdm = random.randint(0, 9)
        if rdm < 2:
            self.socket.sendto(ack.encode(), address)
            print(colored(f"Se envia el ACK a {address} con el numero de secuencia {seq_number}\n", "yellow"))
        else:
            print(colored(f"Se perdio el ACK con el numero de secuencia {seq_number}\n", "red"))

    def send_data(self, message, address):
        print(f"n: {self.n}, base: {self.base}, signumsec: {self.signumsec}\n")
        encoded_msg = message.encode()
        
        if self.signumsec <= self.base + self.n - 1:
            # print(colored(f"Sending {message}\nto {address}\n", "green"))            
            # self.socket.sendto(encoded_msg, address)

            rdm = random.randint(0, 9)
            if rdm < 2:
                print(colored(f"Sending {message}\nto {address}\n", "green"))            
                self.socket.sendto(encoded_msg, address)
            else:
                print(colored(f"Lost {message}\nto {address}\n", "red"))
            
            self.messages[self.signumsec] = encoded_msg
            self.signumsec += 1

            # Intentamos recibir un ACK de forma no bloqueante que nos permita mover la ventana.
            self.socket.setblocking(False)
            self.recv_ack(self.base)

        else:
            print(colored("Ventana llena", "red"))
            print(colored(f"Lost {message}\nto {address}\n", "red"))
            self.socket.setblocking(True)

            # Esperamos por un ACK de forma bloqueante que nos permita mover la ventana.
            # Cuando llega el ACK reenviamos el paquete que quedo fuera de la ventana.
            if self.recv_ack(self.base):
                print(colored(f"Sending {message}\nto {address}\n", "green"))
                self.socket.sendto(encoded_msg, address)
                self.messages[self.signumsec] = encoded_msg
                self.signumsec += 1
            else:
                # Se recibio un ACK repetido. Por ejemplo: Inicialmente base = 0, signumsec = 1.
                # 1) Enviamos el pkt0.
                # 2) Enviamos el pkt1.
                # 3) Recbimos ack0 con numero de secuencia 1 (proximo pkt esperado). Actualizamos base = 1.
                # 4) Ocurre un timeout prematuro debito al pkt 1. Reenviamos el pkt 1.
                # 5) Recibimos ack0 con numero de secuencia 1 (proximo pkt esperado). 
                
                # Luego, no actualizamos la base ya que es un acknowledge repetido.
                self.retransmitir_paquetes(address)

                # Esperamos por un ACK de forma bloqueante que nos permita mover la ventana.
                # Cuando llega el ACK reenviamos el paquete que quedo fuera de la ventana.
                if self.recv_ack(self.base):
                    print(colored(f"Sending {message}\nto {address}\n", "green"))
                    self.socket.sendto(encoded_msg, address)
                    self.messages[self.signumsec] = encoded_msg
                    self.signumsec += 1

        # Puede pasar que la diferencia no sea mayor a 0.0001 y al final no se envien todos los paquetes, incluyendo el 
        # de tipo END. Esto como consecuencia deja bloqueado al cliente.

        # Si aumentamos 0.0001 a 0.000001 ya no tenemos este problema.
        print(f"Timeout: {time.time()} - {self.lastackreceived} = {time.time()-self.lastackreceived}\n")
        if(time.time()-self.lastackreceived > 0.000001):
            self.retransmitir_paquetes(address)

    def recv_ack(self, base):
        """
        Recibe un ACK.

        Parametros:
        - base: Numero de secuencia del paquete no reconocido mas antiguo.

        Devuelve:
        - True si el numero de secuencia del ACK recibido coincide con el numero de secuencia base + 1 (proximo paquete esperado).
        - False en caso contrario.
        """
        try:   
            encoded_msg, _ = self.socket.recvfrom(MAX_LENGTH * 2)
            msg = Message.decode(encoded_msg)

            print(colored(f"Llega un ACK con numero de secuencia {msg.sequence_number} (proximo paquete esperado).", "yellow"))

            if msg.sequence_number < base + 1:
                print(colored(f"No actualizamos la base (llego un ACK repetido).\n", "yellow"))
                return False

            print(colored(f"Actualizamos la base.\n", "yellow"))
            self.base = msg.sequence_number
            self.lastackreceived = time.time() # Reiniciamos el timer cuando llega un ACK
            return True
        
        except BlockingIOError:
            pass

    def retransmitir_paquetes(self, address):
        """
        Retransmite los paquetes que ya han sido enviados pero todavia no se han reconocido. Esto es
        el intervalo [base, signumsec-1].
        """
        print(colored("-------------------------------------", "blue"))
        print(colored(f"Reenviando paquetes con numero de secuencia [{self.base}, {self.signumsec-1}]\n", "blue"))
        for i in range(self.base, self.signumsec):
            print(colored(f"Re-sending {Message.decode(self.messages[i])}\nto {address}\n", "blue"))
            self.socket.sendto(self.messages[i], address)
        print(colored("-------------------------------------\n", "blue"))
    
    def close(self):
        self.socket.close()