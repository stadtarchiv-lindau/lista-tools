import os
import sys
import shutil
import re
import csv
import click
import requests
import subprocess
import pandas as pd
from prettytable import PrettyTable, DOUBLE_BORDER
from packaging import version as pv
from pathlib import Path

WORKING_DIR = Path.cwd()
VERSIONFILE_URL = r'https://github.com/stadtarchiv-lindau/lista-tools/releases/latest/download/VERSION'

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # noinspection PyProtectedMember
    bundle_dir = Path(sys._MEIPASS)
    executable_path = Path(sys.executable).parent
    executable_name = Path(sys.executable).name
    update_script = 'update.exe'
    is_bundled = True
else:
    bundle_dir = Path(__file__).parent
    executable_path = Path(__file__).parent
    executable_name = Path(__file__).name
    update_script = 'update.py'
    is_bundled = False


def get_element_type(path):
    """
    Used for table in batch_prefix()

    :param path: Path to element in filesystem
    :return: String of what the element is
    """
    if Path.is_dir(path):
        return "Directory"
    elif Path.is_file(path):
        return "File"
    elif Path.is_symlink(path):
        return "Symlink"
    else:
        return "Other"


def get_version():
    try:
        with open(bundle_dir / 'VERSION') as versionfile:
            installed_version_str = versionfile.read()
            installed_version = pv.parse(installed_version_str)
    except FileNotFoundError as FNFE:
        click.echo(f"[lista-tools]: An exception occurred when reading the local versionfile.")
        click.echo(f"{FNFE}")
        installed_version = None
        installed_version_str = None

    try:
        r = requests.get(VERSIONFILE_URL)
        available_version_str = r.content.decode().strip()  # decodes bytes object to str
        available_version = pv.parse(available_version_str)
    except requests.RequestException as RE:
        click.echo(f"[lista-tools]: An Error occurred when fetching the newest version. ")
        click.echo(f"{RE}")
        available_version = None
        available_version_str = None

    return (installed_version, installed_version_str), (available_version, available_version_str)


def update(forced):
    try:
        with open(bundle_dir / 'VERSION') as versionfile:
            installed_version_str = versionfile.read()
            installed_version = pv.parse(installed_version_str)
    except FileNotFoundError as FNFE:
        click.echo(f"[lista-tools]: An exception occurred when reading the local versionfile.")
        click.echo(f"{FNFE}")
        installed_version = None
        installed_version_str = None

    try:
        r = requests.get(VERSIONFILE_URL)
        available_version_str = r.content.decode().strip()  # decodes bytes object to str
        available_version = pv.parse(available_version_str)
    except requests.RequestException as RE:
        click.echo(f"[lista-tools]: An Error occurred when fetching the newest version. ")
        click.echo(f"{RE}")
        available_version = None
        available_version_str = None

    if installed_version < available_version:
        click.echo(f"[lista-tools]: A newer version is available.")

    if (installed_version < available_version) or forced:
        click.echo(f"[lista-tools]: Installed version: {installed_version_str}")
        click.echo(f"[lista-tools]: Version available: {available_version_str}")
        if click.confirm("[lista-tools]: Do you want to update?"):  # returns True if user confirms
            click.echo("[lista-tools]: Starting update. Please open lista-tools again after the update has finished.")
            if is_bundled:
                subprocess.Popen([bundle_dir / update_script, executable_path])
            else:
                subprocess.Popen(['python', bundle_dir / update_script, executable_path])
            sys.exit()

    return (installed_version, installed_version_str), (available_version, available_version_str)


@click.group()
def main():
    pass


@click.command()
def force_update():
    """
    Forces an update, even if no newer version is available
    """
    update(forced=True)


@click.command()
def version():
    """
    Prints the currently installed version.
    """
    installed_version_str = version_info[0][1]
    available_version_str = version_info[1][1]

    click.echo("------------------------------")
    if installed_version_str is None:
        click.echo(f"Installed version: Error getting installed version")
    else:
        click.echo(f"Installed version: {installed_version_str}")

    if available_version_str is None:
        click.echo(f"Newest version available: Error getting newest version")
    else:
        click.echo(f"Newest version available: {available_version_str}")
    click.echo("------------------------------")


@click.command()
@click.argument('input', type=click.Path(exists=True, dir_okay=False))
@click.option('-o', '--output', 'output', type=str, default='output.csv', help="The name of the output file. If not "
              "passed, file will be called 'output.csv'")
@click.option('-F', '--remove-folders', 'folders', is_flag=True, default=False, help="Removes all rows containing "
              "information on folders")
def droid_csv(input, output, folders):
    """
    Formats output csv from DROID to fit in LIStA Excel template.

    INPUT is the path to the input file. If no absolute path is given, the working directory will be used.
    """
    output_filename = os.path.basename(output)  # gets file name in case user passes a full output path

    with open(input, 'r', encoding='utf8') as f:
        click.echo(f"[lista-tools]: Opened input file")
        try:
            df = pd.read_csv(f)

        # had some problems in the past with files having more data columns than headers, which causes the parser to not
        # work. current fix is to manually add more header columns. this mostly happens with csv's containing data on
        # ~$xxx.doc lock files generated by Microsoft products, as DROID recognizes them to have multiple file formats
        # see .test/exdir_with_bug.csv
        except pd.errors.ParserError as pe:
            click.echo(f"[lista-tools]: An error occurred: {pe}")
            click.echo(f"[lista-tools]: This is most likely due to some rows having not enough header columns. "
                       f"Try editing the csv file accordingly.")
            sys.exit()
        click.echo(f"[lista-tools]: Loaded data to DataFrame")

    if folders:  # removes rows that contain folders
        df = df[df["TYPE"].str.contains("Folder") == False]
        click.echo(f"[lista-tools]: Removed rows with folders")
        click.echo(f"[lista-tools]: Corrected index")

    df.index += 1
    df = df.astype({'SIZE': 'Int64', 'ID': 'Int64', 'PARENT_ID': 'Int64', 'FORMAT_COUNT': 'Int64'})  # removes decimals
    click.echo(f"[lista-tools]: Formatted numbers as integers")
    df = df.drop(['URI', 'FILE_PATH', 'METHOD', 'STATUS'], axis=1)  # removes columns not present in template
    click.echo(f"[lista-tools]: Dropped unused columns")

    if os.path.exists(output):
        click.confirm(f"[lista-tools]: The file '{output_filename}' already exists. "
                      "Do you want to overwrite?", abort=True)

    click.echo("\n")
    click.echo(df.head())  # prints preview of output
    click.echo("\n")

    with open(output, 'w', encoding='utf8') as f:
        # csv.QUOTE_ALL to prevent issues with whitespace characters in data
        # header=False removes header row, since the Excel template has its own header row
        df.to_csv(f, quoting=csv.QUOTE_ALL, lineterminator='\n', header=False)
        click.echo(f"[lista-tools]: Saved successfully as '{output_filename}'")


@click.command()
@click.option('-R', '--no-recursion', 'no_recursion', is_flag=True, default=False, help="Will only extract folders "
              "once")
def exdir(no_recursion):
    """
    Extracts all folders inside the working directory and adds the folder name as a prefix to its contents
    Will repeat this process until there are only files in the working directory, can be disabled with the '-R' flag
    """
    def extract():
        for directory in Path.iterdir(WORKING_DIR):
            # files can be skipped, as on the first iteration they are already in WORKING_DIR and don't need to be moved
            # and for all subsequent calls the previous iteration has already moved them
            if Path.is_file(directory):
                continue

            for element in Path.iterdir(directory):
                new_name = f"{directory.name.upper()}_ {element.name}"
                (WORKING_DIR / directory / element).rename(WORKING_DIR / directory / new_name)
                shutil.move(WORKING_DIR / directory / new_name, WORKING_DIR)
                click.echo(f"[lista-tools]: Moved: ./{directory.name}/{element.name} -> ./{new_name}")

            Path.rmdir(directory)

        if no_recursion:
            return

        for element in Path.iterdir(WORKING_DIR):
            if Path.is_dir(element):
                click.echo(f"[lista-tools]: Extracting directory: ./{element.name}")
                extract()
                break

    # calls function for the first time
    extract()


@click.command()
@click.option('-S', '--no-space', 'no_space', is_flag=True, default=False, help="Does not add a space after the prefix")
def rename(no_space):
    """
    Renames all files and directories in the working directory by adding a prefix to them.
    """
    change_prefix = True
    prefix = None

    while True:
        if change_prefix:
            prefix = click.prompt("[lista-tools]: Please enter a prefix to add")
            change_prefix = False

        table = PrettyTable(["ID", "Old filename", "New filename", "Type"])  # table to show before vs after
        for idx, element in enumerate(Path.iterdir(WORKING_DIR), 1):  # uses idx as ID; starts at 1
            if no_space:
                new_name = f"{prefix}{element.name}"
            else:
                new_name = f"{prefix} {element.name}"

            element_type = get_element_type(WORKING_DIR / element)
            table.add_row([idx, element.name, new_name, element_type])

        table.align = "l"
        table.align["ID"] = "r"
        table.set_style(DOUBLE_BORDER)
        click.echo(table)

        click.echo(f"[lista-tools]: Do you want to apply the changes?")
        user_choice = click.prompt("[Y] Yes, apply   [N] No, change the prefix   [S] Toggle --no-space  "
                                   "[C] Cancel").casefold()[0]
        match user_choice:
            case 'y':
                break
            case 'n':
                change_prefix = True
                continue
            case 's':
                no_space = not no_space
                continue
            case _:
                click.echo(f"[lista-tools]: Aborting")
                sys.exit()

    for element in Path.iterdir(WORKING_DIR):
        if no_space:
            new_name = f"{prefix}{element.name}"
        else:
            new_name = f"{prefix} {element.name}"

        (WORKING_DIR / element).rename(WORKING_DIR / new_name)
        click.echo(f"[lista-tools]: Renamed: {element.name} -> {new_name}")


@click.command()
def clean_filenames():
    """
    Cleans up filenames by substituting all non-alphanumerical characters with '_'
    Also replaces the German Umlaute with their alphanumerical counterparts
    """
    substitutions = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
        "Ä": "Ae",
        "Ö": "Oe",
        "Ü": "Ue",
    }

    for element in Path.iterdir(WORKING_DIR):
        name = re.sub(r"[^a-zäöüßA-ZÄÖÜ0-9_-]", '_', element.stem)
        for pattern, replacement in substitutions.items():
            name = re.sub(pattern, replacement, name)

        click.echo(f'[lista-tools]: ./{element.parent.stem}/{element.stem} -> ./{element.parent.stem}/{name}')
        element.rename(element.with_stem(name))


main.add_command(droid_csv)
main.add_command(exdir)
main.add_command(version)
main.add_command(rename)
main.add_command(clean_filenames)
main.add_command(force_update)

if __name__ == '__main__':
    version_info = update(forced=False)  # checks for updates before running
    main()
