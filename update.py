import sys
import time
import requests
import hashlib
from pathlib import Path
from ast import literal_eval
from progress.bar import ChargingBar


class Updater:
    def __init__(self):
        self.exec_path = Path(sys.argv[1])
        self.exec_path_old = Path(f"{self.exec_path}.old")
        self.exec_path_new = Path(f"{self.exec_path}.new")
        self.params = literal_eval(sys.argv[2])  # literal_eval to convert str representation of a dict to a dict
        self.params['target_dir'] = Path(self.params.get('target_dir'))
        self.binary_url = r'https://github.com/stadtarchiv-lindau/lista-tools/releases/latest/download/lista-tools.exe'
        self.sha256_url = r'https://github.com/stadtarchiv-lindau/lista-tools/releases/latest/download/SHA256'
        self.update()

    def print_debug(self, text):
        if self.params.get('logging') in 'debug':
            print(f"DEBUG: {text}")

    def print_info(self, text, end='\n', flush=False):
        if self.params.get('logging') in ('debug', 'full'):
            print(text, end=end, flush=flush)

    def report_warning(self, text):
        if self.params.get('logging') in ('debug', 'full', 'warn'):
            print(f"WARNING: {text}")

    def report_error(self, text, error, abort=False):
        if self.params.get('logging') in ('debug', 'full', 'warn', 'error'):
            print(f"ERROR: {text}")
            print(error)
        if abort is True:
            sys.exit()

    def confirm(self, text):
        if self.params.get('noconfirm'):
            return True
        self.print_info(f"{text} [y/N]: ", end='')
        choice = input()[0].casefold()
        self.print_info("")
        match choice:
            case 'y':
                return True
            case _:
                return False

    def abort(self):
        self.print_info("Aborting update!")
        sys.exit()

    def _rename(self, src: Path, dst: Path):
        try:
            self.print_info(f"Renaming: {src.name} -> {dst.name}")
            if dst.exists():
                if not self.confirm(f"{dst.name} exists. Do you want to overwrite?"):
                    self.abort()
            src.rename(dst)
        except OSError as OSE:
            self.report_error("An error occurred when renaming the temporary files. Please try again or manually "
                              "download the newest version from GitHub and delete the temporary files.", OSE,
                              abort=True)

        time.sleep(1)

    def update(self):
        self.print_info("Getting latest hash")
        self.print_info(f"Download source: {self.sha256_url}")
        try:
            r_sha256 = requests.get(self.sha256_url)
            expected_hash = r_sha256.content.decode().strip()
            self.print_info(f"Latest build hash: {expected_hash}")
        except requests.RequestException as RE:
            self.report_error("An error occurred when downloading the latest hash.", RE)
            if not self.confirm("The integrity of the file will not be able to be verified. Do you still want to "
                                "update? (NOT RECOMMENDED)"):
                self.abort()
            expected_hash = None

        self.print_info("Downloading binary")
        self.print_info(f"Download source: {self.binary_url}")
        try:
            r_binary = requests.get(self.binary_url, stream=True)
            total_length = int(r_binary.headers.get('content-length'))
            bytes_done = 0
            response_list = []
            for chunk in r_binary.iter_content(chunk_size=4096):
                bytes_done += len(chunk)
                response_list.append(chunk)
                p_bar_progress = int(50 * bytes_done / total_length)
                p_bar_percentage = round((100 * bytes_done / total_length), 1)
                self.print_info(f"\r[{'═' * p_bar_progress + ' ' * (50 - p_bar_progress)}] {p_bar_percentage}%", end='',
                                flush=True)
            self.print_info("")
        except requests.RequestException as RE:
            self.report_error("An error occurred when downloading the latest binary", RE, abort=True)

        # noinspection PyUnboundLocalVariable
        downloaded_data = b''.join(response_list)
        self.print_info("Verifying hashes")
        if expected_hash is None:
            pass
        elif expected_hash != hashlib.sha256(downloaded_data).hexdigest():
            if not self.confirm("The latest build hash does not match the downloaded file. The file may be compromised."
                                " Only proceed if you know what you are doing. Do you still want to update? "
                                "(NOT RECOMMENDED)"):
                self.abort()

        self.print_info("Hashes match. Writing data to file")
        try:  # saving downloaded file as .exe.new
            if self.exec_path_new.exists():
                if not self.confirm(f"{self.exec_path_new.name} exists. Do you want to overwrite?"):
                    self.abort()

            with open(self.exec_path_new, 'wb') as newfile:
                newfile.write(downloaded_data)
            self.print_info(f"Saved as {self.exec_path_new.name}")
        except OSError as OSE:
            self.report_error("An error occurred when saving the temporary file. Please try again or manually download "
                              "the newest version from GitHub and delete the temporary files.", OSE, abort=True)

        self._rename(self.exec_path, self.exec_path_old)  # renaming .exe -> .exe.old
        self._rename(self.exec_path_new, self.exec_path)  # renaming .exe.new -> .exe

        try:  # deleting .exe.old
            self.print_info(f"Deleting {self.exec_path_old.name}")
            self.exec_path_old.unlink()
        except OSError as OSE:
            self.report_error("An error occurred when removing the temporary file. Please try again or remove the file "
                              "manually", OSE)

        self.print_info("Update complete. Press Enter to exit", end='', flush=True)
        self.print_info("")
        sys.exit()


if __name__ == '__main__':
    Updater()
