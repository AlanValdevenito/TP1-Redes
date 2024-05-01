from stop_and_wait import StopAndWaitProtocol
from gbn import GBNProtocol

STOP_AND_WAIT = '1'


class ProtocolFactory:
    @staticmethod
    def create_protocol(protocol_type, ip, port):
        if protocol_type == STOP_AND_WAIT:
            return StopAndWaitProtocol(ip, port)
        else:
            return GBNProtocol(ip, port)
