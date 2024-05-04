from stop_and_wait import StopAndWaitProtocol
from gbn import GBNProtocol
from config import STOP_AND_WAIT


class ProtocolFactory:
    @staticmethod
    def create_protocol(protocol_type, ip, port, logger):
        if protocol_type == STOP_AND_WAIT:
            return StopAndWaitProtocol(ip, port, logger)
        else:
            return GBNProtocol(ip, port, logger)
