import os
import sys
import time
import requests
import hashlib
from pathlib import Path

executable = Path(sys.argv[1])
executable_old = Path(f'{executable}.old')
executable_new = Path(f'{executable}.new')

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
try:
    if not executable_new.exists():
        with open(executable_new, 'wb') as downloadfile:
            downloadfile.write(downloaded_data)
        print(f"[lista-tools]: Saved as {executable_new.name}")
    else:
        choice = input(f"[lista-tools]: {executable_new.name} exists. Do you want to overwrite? [y/N]")[0].casefold()
        match choice:
            case 'y':
                with open(executable_new, 'wb') as downloadfile:
                    downloadfile.write(downloaded_data)
            case _:
                print(f"[lista-tools]: Aborting update.")
                sys.exit()

        print(f"[lista-tools]: Saved as {executable_new.name}")
except OSError as OSE:
    print(f"[lista-tools]: An error occurred when saving the temporary file. Please try again or manually download the "
          f"newest version from GitHub and delete the temporary files.")
    print(OSE)
    sys.exit()

try:
    print(f"[lista-tools]: Renaming: {executable.name} -> {executable_old.name}")
    if not executable_old.exists():
        executable.rename(executable_old)
    else:
        choice = input(f"[lista-tools]: {executable_old.name} exists. Do you want to overwrite? [y/N]")[0].casefold()
        match choice:
            case 'y':
                executable.rename(executable_old)
            case _:
                print(f"[lista-tools]: Aborting update.")
                sys.exit()
    time.sleep(1)
except OSError as OSE:
    print(f"[lista-tools]: An error occurred when renaming the temporary file. Please try again or manually download "
          f"the newest version from GitHub and delete the temporary files.")
    print(OSE)
    sys.exit()

try:
    # no need to check if executable already exists because it would have been renamed earlier
    print(f"[lista-tools]: Renaming: {executable_new.name} -> {executable.name}")
    executable_new.rename(executable)
    time.sleep(1)
except OSError as OSE:
    print(f"[lista-tools]: An error occurred when renaming the temporary file. Please try again or manually download "
          f"the newest version from GitHub and delete the temporary files.")
    print(OSE)
    sys.exit()

try:
    print(f"[lista-tools]: Deleting {executable_old.name}")
    os.remove(f'{executable_old}')
except OSError as OSE:
    print(f"[lista-tools]: An error occurred when removing the temporary file. Please try again or remove the file "
          f"manually.")
    print(OSE)

print(f"[lista-tools]: Update complete. Please press Enter.")
