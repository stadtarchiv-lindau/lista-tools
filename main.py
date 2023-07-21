import sys
import re
import csv
import click
import requests
import subprocess
import pandas as pd
from prettytable import PrettyTable, DOUBLE_BORDER
from packaging import version
from pathlib import Path


class ListaTools:
    def __init__(self):
        self.params = {}
        self.target_dir = None
        self.versionfile_url = r'https://github.com/stadtarchiv-lindau/lista-tools/releases/latest/download/VERSION'
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):  # checks if script is running from binary or .py
            self.is_bundled = True
            # noinspection PyProtectedMember
            # sys._MEIPASS contains other files bundled with the script
            self.versionfile_path = Path(sys._MEIPASS) / 'VERSION'
            self.executable_path = Path(sys.executable)
            # noinspection PyProtectedMember
            self.update_path = Path(sys._MEIPASS) / 'update.exe'
        else:
            self.is_bundled = False
            self.versionfile_path = Path(__file__).parent / 'VERSION'
            self.executable_path = Path(__file__)
            self.update_path = Path(__file__).parent / 'update.py'

        self.installed_version = self._get_installed_version()
        self.newest_version = self._get_newest_version()

    def insert_params(self, logging, noconfirm, target_dir):
        """Used to insert parameters after cli() has been called

        :param str logging: Verbosity of script; can be one of [debug | full | warn | error | none]
        :param bool noconfirm: Skips all confirmation prompts to allow script to be run without any user input
        :param pathlib.Path target_dir: The directory the script will be working in, defaults to working directory
        :return: N/A
        """
        self.params.update({'logging': logging,
                            'noconfirm': noconfirm,
                            'target_dir': target_dir,
                            })
        self.target_dir = self.params.get('target_dir')  # extracted to variable for cleaner code
        self.print_debug(f"Logging: {self.params.get('logging')}")
        self.print_debug(f"Noconfirm: {self.params.get('noconfirm')}")
        self.print_debug(f"Target directory: {self.params.get('target_dir')}")

    def update_check(self, force):
        """Checks if an update is available and calls ListaTools.update() if it is

        :param bool force: Always opens update dialogue
        :return: N/A
        """
        if force:
            self.print_info("Forcing update")
            self.update()
        elif self._newer_version_available():
            self.print_info("A newer version is available")
            self.update()

    def print_debug(self, text):
        """Prints text if logging level is 'debug'

        :param any text: What to print
        :return: N/A
        """
        if self.params.get('logging') in 'debug':
            print(f"DEBUG: {text}")

    def print_info(self, text, end='\n', flush=False):
        """Prints text if logging level is one of [debug | full]

        :param any text: What to print
        :param str end: passed to print()
        :param bool flush: passed to print()
        :return: N/A
        """
        if self.params.get('logging') in ('debug', 'full'):
            print(text, end=end, flush=flush)

    def report_warning(self, text):
        """Prints text if logging level is one of [debug | full | warn]

        :param any text: What to print
        :return: N/A
        """
        if self.params.get('logging') in ('debug', 'full', 'warn'):
            print(f"WARNING: {text}")

    def report_error(self, text, error, abort=False):
        """Prints text and error if logging level is one of [debug | full | warn | error]
        Exits afterwards if abort=True

        :param any text: What to print
        :param BaseException error: The error to print
        :param bool abort: Whether to exit after printing
        :return: N/A
        """
        if self.params.get('logging') in ('debug', 'full', 'warn', 'error'):
            print(f"ERROR: {text}")
            print(error)
        if abort is True:
            sys.exit()

    def confirm(self, text):
        """Prints text and asks user to confirm, e.g. "Do you want to overwrite? [y/N]: "

        :param any text: The text to print before waiting for user to confirm
        :return bool: True if user confirmed, False if not
        """
        if self.params.get('noconfirm'):
            return True
        self.print_info(f"{text} [y/N]: ", end='')
        choice = input()[0].casefold()
        match choice:
            case 'y':
                return True
            case _:
                return False

    def abort(self):
        """Prints abort message and stops execution

        :return: N/A
        """
        self.print_info("Aborting!")
        sys.exit()

    def _get_installed_version(self):
        """Reads installed version from local versionfile

        :return str: A string of the installed version or 'Error' if any error occurred
        """
        try:
            with open(self.versionfile_path) as versionfile:
                content = versionfile.read().strip()
            return content
        except FileNotFoundError as FNFE:
            self.report_error("An error occurred when reading the local versionfile. "
                              "Your installation may be damaged.", FNFE)
            return 'Error'

    def _get_newest_version(self):
        """Fetches the newest available version from GitHub

        :return str: A string of the available version or 'Error' if any error occurred
        """
        try:
            r = requests.get(self.versionfile_url)
            content = r.content.decode().strip()  # decodes bytes object to str
            return content
        except requests.RequestException as RE:
            self.report_error("An error occurred when fetching the newest version.", RE)
            return 'Error'

    def _newer_version_available(self):
        """Compares the installed and available version

        :return bool: True if newer version is available, False if not
        """
        try:
            if version.parse(self.newest_version) > version.parse(self.newest_version):
                return True
            else:
                return False
        except version.InvalidVersion:
            pass

    def update(self):
        """Confirms if user wants to update, and calls update script if that is the case

        :return NoneType: None if user refuses update
        """
        self.print_info(f"Installed version: {self.installed_version}")
        self.print_info(f"Available version: {self.newest_version}")
        if not self.confirm("Do you want to update?"):
            return
        self.print_info("Starting update. Please reopen lista-tools after the update has finished.")
        passed_params = self.params
        passed_params['target_dir'] = str(self.target_dir)
        if self.is_bundled:
            self.print_debug(str(passed_params))
            subprocess.Popen([self.update_path, self.executable_path, str(passed_params)])
        # else:
            # subprocess.Popen(['python', self.update_path, self.executable_path, str(self.params)])

        sys.exit()

    @staticmethod
    def get_element_type(path):
        """Returns string of type that the element is

        :param pathlib.Path path: Path to the element to be analyzed
        :return str: String of element type
        """
        if Path.is_dir(path):
            return "Directory"
        elif Path.is_file(path):
            return "File"
        elif Path.is_symlink(path):
            return "Symlink"
        else:
            return "Other"

    def print_version(self):
        """See caller function documentation"""
        self.print_info("------------------------------")
        self.print_info(f"Installed version: {self.installed_version}")
        self.print_info(f"Newest version available: {self.newest_version}")
        self.print_info("------------------------------")

    def clean_filenames(self):
        """See caller function documentation"""
        substitutions = {
            "ä": "ae",
            "ö": "oe",
            "ü": "ue",
            "ß": "ss",
            "Ä": "Ae",
            "Ö": "Oe",
            "Ü": "Ue",
        }
        table = PrettyTable(['ID', 'Original filename', 'Cleaned filename', 'Type'])
        changes = []
        for idx, element in enumerate(Path.iterdir(self.params.get('target_dir')), 1):
            new_stem = re.sub(r"[^a-zäöüßA-ZÄÖÜ0-9_-]", '_', element.stem)
            for pattern, replacement in substitutions.items():
                new_stem = re.sub(pattern, replacement, new_stem)
            changes.append((element, element.with_stem(new_stem)))
            table.add_row([idx, element.name, new_stem + element.suffix, self.get_element_type(element)])

        table.align = 'l'
        table.align['ID'] = 'r'
        table.set_style(DOUBLE_BORDER)
        self.print_info(table)
        if self.confirm("Do you want to apply the changes?"):
            try:
                self.print_info(f"Renaming: 0/{len(changes)}", end='', flush=True)
                for n, tup in enumerate(changes, 1):
                    src, dst = tup
                    self.print_info(f"\rRenaming: {n}/{len(changes)}", end='', flush=True)
                    if src == dst:
                        continue
                    try:
                        src.rename(dst)
                    except OSError as OSE:
                        self.report_error("An error occurred when renaming one of the files. Continuing", OSE)
                        continue
                self.print_info("")
            except OSError as OSE:
                self.report_error("An error occurred when renaming the files", OSE)

    def droid_csv(self, input, output, remove_folders):
        """See caller function documentation

        :param str | pathlib.Path input: Name of input file or path to it
        :param str | pathlib.Path output: Name of input file or path to it
        :param bool remove_folders: Whether to remove folders
        :return: N/A
        """
        src = Path(input)
        if not src.is_absolute():
            src = (self.target_dir / src).absolute()
        dst = Path(output)
        if not dst.is_absolute():
            dst = (self.target_dir / dst).absolute()
        try:
            with open(src, 'r', encoding='utf8') as f:
                df = pd.read_csv(f)
        except OSError as OSE:
            self.report_error("An error occurred when reading the input file", OSE, abort=True)
        except pd.errors.ParserError as PE:
            # had some problems in the past with files having more data columns than headers, which causes the parser to
            # not work. current fix is to manually add more header columns. this mostly happens with csv's containing
            # data on ~$xxx.doc lock files generated by Microsoft products, as DROID recognizes them to have multiple
            # file formats; example file demonstrating bug in .test/exdir_with_bug.csv
            self.report_error("An error occurred when parsing the input file. This may be caused by some rows having "
                              "more entries than there are header columns. For more info see the droid-csv "
                              "documentation on GitHub (https://github.com/stadtarchiv-lindau/lista-tools#droid-csv)",
                              PE, abort=True)

        self.print_info("Loaded csv into DataFrame")
        if remove_folders:  # removes rows that contain folders
            df = df[df['TYPE'].str.contains("Folder") == False]
            self.print_info("Removed rows with folders")

        # noinspection PyUnboundLocalVariable
        df.index += 1
        # removes decimals
        df = df.astype({'SIZE': 'Int64', 'ID': 'Int64', 'PARENT_ID': 'Int64', 'FORMAT_COUNT': 'Int64'})
        self.print_info("Formatted numbers as integers")
        df = df.drop(['URI', 'FILE_PATH', 'METHOD', 'STATUS'], axis=1)  # removes columns not present in template
        self.print_info("Dropped unused columns")

        self.print_info(df.head())

        if dst.exists():
            if not self.confirm(f"{dst.name} exists. Do you want to overwrite?"):
                self.abort()

        try:
            with open(dst, 'w', encoding='utf8') as f:
                # csv.QUOTE_ALL to prevent issues with whitespace characters in data
                # header=False removes header row, since the Excel template has its own header row
                df.to_csv(f, quoting=csv.QUOTE_ALL, lineterminator='\n', header=False)
                self.print_info(f"Saved as {dst.name}")
        except OSError as OSE:
            self.report_error("An error occurred when reading the input file", OSE, abort=True)

    def exdir(self, recursion):
        """See caller function documentation

        :param bool recursion: Toggles recursive behaviour
        :return: N/A
        """
        def extract():
            self.print_debug(f"Inside exdir: {self.target_dir}")
            for directory in Path.iterdir(self.target_dir):
                remove_dir = True
                # files can be skipped, as on the first iteration they are already in WORKING_DIR and don't need to be
                # moved and for all subsequent calls the previous iteration has already moved them
                if Path.is_file(directory):
                    continue
                for element in Path.iterdir(directory):
                    dst = self.target_dir / f"{directory.name.upper()}_ {element.name}"
                    try:
                        element.rename(dst)
                        self.print_info(f"Moved: ./{directory.name}/{element.name} -> ./{dst.name}")
                    except OSError as OSE:
                        self.report_error("An error occurred when moving the files", OSE)
                        remove_dir = False  # won't remove parent if moving failed on child
                        continue

                if remove_dir is True:
                    Path.rmdir(directory)

            if recursion is False:
                return
            for element in Path.iterdir(self.target_dir):
                if Path.is_dir(element):
                    self.print_info(f"Found more directories, extracting them")
                    extract()
                    break

        # calls function for the first time
        extract()

    def rename(self, prefix):
        """See caller function documentation

        :param any prefix: The prefix to add
        :return: N/A
        """
        table = PrettyTable(["ID", "Old filename", "New filename", "Type"])
        for idx, element in enumerate(Path.iterdir(self.target_dir), 1):  # uses idx as ID; starts at 1
            new_name = f"{prefix}{element.name}"
            element_type = self.get_element_type(element)
            table.add_row([idx, element.name, new_name, element_type])

        table.align = 'l'
        table.align['ID'] = 'r'
        table.set_style(DOUBLE_BORDER)
        self.print_info(table)
        if not self.confirm("Do you want to apply these changes?"):
            self.abort()

        for element in Path.iterdir(self.target_dir):
            element.rename(f"{prefix}{element.name}")
            self.print_info(f"Renamed: {element.name} -> {prefix}{element.name}")

# 'logging': none | error | warn | full | debug


if __name__ == '__main__':
    @click.group(invoke_without_command=True, no_args_is_help=True)
    @click.option('-l', '--logging', type=click.Choice(['none', 'error', 'warn', 'full', 'debug'],
                  case_sensitive=False), default='full', help="The level of verbosity of the script. 'none' prints "
                  "nothing, 'error' only errors, 'warn' warnings and errors, 'full' prints everything, 'debug' prints "
                  "additional debug info. When using 'none', 'error' or 'warn' be sure to also use --noconfirm to avoid"
                  " issues with being asked for confirmation")
    @click.option('-y', '--noconfirm', is_flag=True, default=False, help="Automatically confirms all prompts for you")
    @click.option('--target-dir', type=click.Path(exists=True, file_okay=False, writable=True, resolve_path=True,
                  path_type=Path), default=Path.cwd(), help="The directory that the commands will be executed in. If "
                  "the option is not passed, the directory in which you opened the script will be used")
    @click.option('-U', '--force-update', 'updateflag', is_flag=True, default=False, help="Opens the update dialogue "
                  "even if no newer version is available")
    @click.option('-v', '--version', 'versionflag', is_flag=True, default=False, help="Prints information about the "
                  "current and available version")
    @click.option('-d', '--debug', is_flag=True, default=False, help="Functionally identical to '-l debug', but "
                  "overwrites it. Implemented for nicer commands")
    def cli(logging, noconfirm, target_dir, updateflag, versionflag, debug):
        if debug is True:
            logging = 'debug'
        ltt.insert_params(logging=logging, noconfirm=noconfirm, target_dir=target_dir)
        if versionflag:
            ltt.print_version()
        ltt.update_check(force=updateflag)

    @cli.command()
    def clean_filenames():
        """Cleans up filenames by substituting all non-alphanumerical characters with '_'.
        Also replaces the German Umlaute with their alphanumerical counterparts (e.g. ä -> ae)
        """
        ltt.clean_filenames()

    @cli.command()
    # paths are passed as str, since all checks are done in the function itself
    @click.argument('input')
    @click.option('-o', '--output', default='output.csv', help="The name of the output file, defaults to 'output.csv'")
    # ' /-F' defines -F as alias for the --remove-folders
    @click.option(' /-F', '--keep-folders/--remove-folders', 'remove_folders', default=False, help="Removes all rows "
                  "containing information on folders, defaults to '--keep-folders'")
    def droid_csv(input, output, remove_folders):
        """Formats a csv file made by DROID to fit in the LIStA Excel template

        INPUT is the path to the input file
        """
        ltt.droid_csv(input=input, output=output, remove_folders=remove_folders)

    @cli.command()
    # ' /-R' defines -R as alias for the --no-recursion
    @click.option(' /-R', '--recursion/--no-recursion', 'recursion', default=True, help="Toggles recursive behaviour. "
                  "If '--no-recursion' is passed, only the top layer of directories will be , defaults to "
                  "'--recursion'")
    def exdir(recursion):
        """Extracts all folders inside the target directory and adds the name of the parent folder as a prefix to the
        extracted element. If recursion is turned on, this will repeat until there are only files left in the target
        """
        ltt.exdir(recursion=recursion)

    @cli.command()
    @click.argument('prefix')
    def rename(prefix):
        """Adds the passed prefix to all elements in the target directory

        PREFIX is the prefix to add
        """
        ltt.rename(prefix=prefix)

    # __init__ is run outside of cli() to avoid having to return ltt,
    # since params are only known after cli() runs
    try:
        ltt = ListaTools()
        cli()
    except KeyboardInterrupt as KI:
        print("Interrupted by user!")
        sys.exit()
