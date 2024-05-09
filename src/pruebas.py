from lib.client import Client
from lib.config import IP, SERVER_PORT, PORT
from lib.config import STOP_AND_WAIT, UPLOAD, DOWNLOAD
from lib.utils import parse_server_args
import subprocess
import time
import os
import matplotlib.pyplot as plt
import numpy as np

GO_BACK_N = '0'
SERVER_ADDRESS = (IP, SERVER_PORT)
N_CLIENTS = 3
NUMBER_OF_FILES = 5
files = ['file1', 'file2', 'file4', 'file8', 'file16']


def test(operation, protocol):
    args = parse_server_args()
    args.protocol = protocol

    proc = subprocess.Popen(['python3', 'start-server', '-P', protocol])

    times = []
    size = {}
    for f in files:
        size[f] = os.path.getsize(f)

    for f in files:
        client = Client(IP, PORT, args)
        start = time.time()
        if operation == UPLOAD:
            client.upload(f, f + f"_{operation}", SERVER_ADDRESS)
        elif operation == DOWNLOAD:
            client.download(f + f"_{operation}",
                            f, SERVER_ADDRESS)
        time_elapsed = time.time() - start
        times.append(time_elapsed)

    os.system(f"kill {proc.pid}")
    return times


def generate_files():
    one_mb_of_data = "A" * 1024 * 1024
    size = 1
    for i in range(NUMBER_OF_FILES):
        print(f"i = {i}")
        with open(f"file{size}", "w") as f:
            for _ in range(size):
                f.write(one_mb_of_data)
        with open(f"server_storage/file{size}", "w") as f:
            for _ in range(size):
                f.write(one_mb_of_data)
        size = size * 2


def delete_files():
    size = 1
    for _ in range(NUMBER_OF_FILES):
        filename = f"file{size}"
        delete_file(filename)
        delete_file(f"{filename}_download")
        delete_file(f"server_storage/{filename}")
        delete_file(f"server_storage/{filename}_upload")
        size = size * 2


def delete_file(filename):
    absolute_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(absolute_path):
        os.remove(absolute_path)


def main():
    generate_files()
    results = {
        'upload': {
            'snw': test(UPLOAD, STOP_AND_WAIT),
            'gbn': test(UPLOAD, GO_BACK_N)
        },
        'download': {
            'snw': test(DOWNLOAD, STOP_AND_WAIT),
            'gbn': test(DOWNLOAD, GO_BACK_N)
        }
    }

    sizes = [1, 2, 4, 8, 16]

    for operation in results:
        x = np.array(sizes)
        y1 = np.array(results[operation]['snw'])
        y2 = np.array(results[operation]['gbn'])

        plt.plot(x, y1, "-b", label="Stop & Wait")
        plt.plot(x, y2, "-r", label="Go Back N")
        plt.legend(loc="upper left")
        title = f'''Tiempo de finalización según
                    tamaño del archivo para {operation}'''
        plt.title(label=title)
        plt.xlabel("Tamaño del archivo (MB)")
        plt.ylabel("Tiempo de finalización (segundos)")
        plt.show()
    delete_files()


if __name__ == "__main__":
    main()
