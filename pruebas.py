from lib.client import Client
from lib.config import IP, SERVER_PORT, PORT, STOP_AND_WAIT, UPLOAD, DOWNLOAD
from lib.utils import parse_server_args
import subprocess, time, os
import matplotlib.pyplot as plt
import numpy as np

GO_BACK_N='0'
SERVER_ADDRESS=(IP, SERVER_PORT)
N_CLIENTS=3

files = ['file.txt', 'file2.txt', 'file4.txt', 'file8.txt', 'file16.txt']

def test(operation, protocol):
    args = parse_server_args()
    args.protocol = protocol

    proc = subprocess.Popen(['python3', 'main_server.py', '-P', protocol])    

    times = []
    size = {}
    for f in files:
        size[f] = os.path.getsize(f)

    for f in files:
        for i in range(1):
            client = Client(IP, PORT + i, args)
            print(f"\nUpload & download tests for client n°{i}:\n")
            start = time.time()
            if operation == UPLOAD:
                client.upload(f, f + f"_{operation}_" + str(i), SERVER_ADDRESS)
            elif operation == DOWNLOAD:
                client.download(f + f"_{operation}_" + str(i), f, SERVER_ADDRESS)
            time_elapsed = time.time() - start
            times.append(time_elapsed)

    os.system(f"kill {proc.pid}")
    return times

def main():
    
    results = {
        'upload' : {
            'snw': test(UPLOAD, STOP_AND_WAIT),
            'gbn': test(UPLOAD, GO_BACK_N)
        },
        'download' : {
            'snw': test(DOWNLOAD, STOP_AND_WAIT),
            'gbn': test(DOWNLOAD, GO_BACK_N)
        }
    }

    sizes = [1,2,4,8,16]
    
    for operation in results:
        x = np.array(sizes)
        y1 = np.array(results[operation]['snw'])
        y2 = np.array(results[operation]['gbn'])

        plt.plot(x, y1, "-b", label="Stop & Wait")
        plt.plot(x, y2, "-r", label="Go Back N")
        plt.legend(loc="upper left")
        plt.title(label= f'Tiempo de finalización según tamaño del archivo para {operation}')
        plt.xlabel("Tamaño del archivo (MB)")
        plt.ylabel("Tiempo de finalización (segundos)")
        plt.show()

main()