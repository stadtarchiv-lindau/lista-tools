import os
import sys
import time
import requests
import hashlib
from pathlib import Path

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # noinspection PyProtectedMember
    try:
        main_executable_path = Path(sys.argv[1])
    except IndexError:
        main_executable_path = Path(sys.executable).parent

else:
    main_executable_path = Path(__file__).parent

BINARY_URL = r'https://github.com/stadtarchiv-lindau/lista-tools/releases/latest/download/lista-tools.exe'
SHA256_URL = r'https://github.com/stadtarchiv-lindau/lista-tools/releases/latest/download/SHA256'

print(f"")
print(f"[lista-tools]: Getting latest hash")
try:
    sha256_response = requests.get(SHA256_URL)
    expected_hash = sha256_response.content.decode().strip()
    print(f"[lista-tools]: Latest build hash: {expected_hash}")

except requests.RequestException as RE:
    print(f"[lista-tools]: An error occurred when downloading the latest hash ({RE})")
    choice = input(f"The integrity of the file will not be able to be verified. Do you still want to update? (NOT "
                   f"RECOMMENDED) [y/N]: ").casefold()[0]
    expected_hash = None
    if not choice == 'y':
        print(f"[lista-tools]: Aborting update.")
        sys.exit()

print(f"[lista-tools]: Downloading new binary")
try:
    binary_response = requests.get(BINARY_URL, stream=True)
    total_length = int(binary_response.headers.get('content-length'))
    bytes_done = 0
    response_list = []
    for chunk in binary_response.iter_content(chunk_size=4096):
        bytes_done += len(chunk)
        response_list.append(chunk)
        done = int(50 * bytes_done / total_length)
        percent = round((100 * bytes_done / total_length), 1)
        print(f"\r[{'═' * done + ' ' * (50 - done)}] {percent}%", end='', flush=True)
    print("")
except requests.RequestException as RE:
    print(f"[lista-tools]: An error occurred when downloading the latest binary ({RE})")
    input(f"[lista-tools]: Press enter to close this window.")
    sys.exit()

downloaded_data = b''.join(response_list)

print(f"[lista-tools]: Verifying hashes")
if expected_hash is None:
    pass
elif expected_hash != hashlib.sha256(downloaded_data).hexdigest():
    choice = input(f"[lista-tools]: The latest build hash does not match the downloaded file. The file may be"
                   f"compromised. Only proceed if you know what you are doing. Do you still want to update? (NOT "
                   f"RECOMMENDED) [y/N]: ").casefold()[0]
    if not choice == 'y':
        print(f"[lista-tools]: Aborting update.")
        sys.exit()

print(f"[lista-tools]: Hashes match. Writing data to file.")
with open(main_executable_path / 'lista-tools.exe.new', 'wb') as downloadfile:
    downloadfile.write(downloaded_data)

print(f"[lista-tools]: Saved as lista-tools.exe.new")
print(f"[lista-tools]: Renaming: lista-tools.exe -> lista-tools.exe.old")
try:
    (main_executable_path / 'lista-tools.exe').rename('lista-tools.exe.old')
except OSError:
    print(f"[lista-tools]: Error: lista-tools.exe not found. Saving downloaded file as lista-tools.exe")
    (main_executable_path / 'lista-tools.exe.new').rename('lista-tools.exe')
    input(f"[lista-tools]: Update complete. Press Enter to close this window.")
    sys.exit()

time.sleep(1)
print(f"[lista-tools]: Renaming: lista-tools.exe.new -> lista-tools.exe")
try:
    (main_executable_path / 'lista-tools.exe.new').rename('lista-tools.exe')
    time.sleep(1)
    print(f"[lista-tools]: Deleting lista-tools.exe.old")
    os.remove(main_executable_path / 'lista-tools.exe.old')
except OSError as OSE:
    print(f"[lista-tools]: An error has occurred when installing. Please either rename the files manually or delete the"
          f"temporary files and restart update. Press Enter to confirm.")
    print(OSE)
    sys.exit()
print(f"[lista-tools]: Update complete. Please press Enter.")
