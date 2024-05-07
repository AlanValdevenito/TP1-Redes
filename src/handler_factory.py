from upload_handler import UploadHandler
from download_handler import DownloadHandler
from config import UPLOAD, DOWNLOAD


class HandleFactory:
    @staticmethod
    def create_handle(
            ip, handle_type, client_address, filename, protocol, logger):
        if handle_type == UPLOAD:
            return UploadHandler(
                ip, client_address, filename, protocol, logger)
        elif handle_type == DOWNLOAD:
            return DownloadHandler(
                ip, client_address, filename, protocol, logger)
        else:
            raise Exception("Invalid handle type")
