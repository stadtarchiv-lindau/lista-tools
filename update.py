import os
import sys
import time

import requests
from pathlib import Path

FILE_DIR = Path(bytes.fromhex(sys.argv[1]).decode())
# url = r'https://raw.githubusercontent.com/sammmsational/lista-tools/master/.pyinstaller/dist/lista-tools.exe'
url = r'http://listatools.kulturlindau.de/lista-tools.exe'

print(f'[lista-tools]: Downloading new binary')
with open(FILE_DIR / 'lista-tools.exe.new', 'wb') as downloadfile:
    r = requests.get(url, stream=True)
    total_length = int(r.headers.get('content-length'))
    bytes_done = 0
    for data in r.iter_content(chunk_size=4096):
        bytes_done += len(data)
        downloadfile.write(data)
        done = int(50 * bytes_done / total_length)
        percent = round((100 * bytes_done / total_length), 1)
        print(f"\r[{'═' * done + ' ' * (50 - done)}] {percent}%", end='', flush=True)

# noinspection PyBroadException
try:
    print(f'[lista-tools]: Download complete. Saved as lista-tools.exe.new')
    print(f'[lista-tools]: Renaming: lista-tools.exe -> lista-tools.exe.old')
    os.rename(FILE_DIR / 'lista-tools.exe', FILE_DIR / 'lista-tools.exe.old')
    time.sleep(1)
    print(f'[lista-tools]: Renaming: lista-tools.exe.new -> lista-tools.exe')
    os.rename(FILE_DIR / 'lista-tools.exe.new', FILE_DIR / 'lista-tools.exe')
    time.sleep(1)
    print(f'[lista-tools]: Deleting lista-tools.exe.old')
    os.remove(FILE_DIR / 'lista-tools.exe.old')
    input(f'[lista-tools]: Update complete. Press Enter to close this window.')
except Exception:
    print(f'[lista-tools]: An error has occured when installing. Please either rename the files manually or delete the'
          f'temporary files and restart update.')
