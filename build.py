import sys
# from datetime import datetime
import PyInstaller.__main__

# now = datetime.now().isoformat(timespec='seconds')  # legacy code from having build date

try:
    with open('VERSION', 'r') as f:
        old_version = f.read()
    no_config = False

    print(f"Previous version: {old_version}")

except FileNotFoundError:
    print("Config file not found. Cannot keep old version number.")
    no_config = True
    old_version = None

new_version = input(f"New version (k to keep): ")

if new_version == "k":
    if no_config:
        print("Config could not be found; old version cannot be copied")
        sys.exit()

    new_version = old_version

with open('VERSION', 'w') as f:
    f.write(new_version)

PyInstaller.__main__.run([
    'update.py',
    '-n', 'update',
    '--distpath', './.pyinstaller/update/dist',
    '--workpath', './.pyinstaller/update/build',
    '--specpath', './.pyinstaller/update',
    '--clean',
    '--onefile',
    '--noconfirm',

])

PyInstaller.__main__.run([
    'main.py',
    '-n', 'lista-tools',
    '--distpath', './.pyinstaller/main/dist',
    '--workpath', './.pyinstaller/main/build',
    '--specpath', './.pyinstaller/main',
    '--clean',
    '--onefile',
    '--noconfirm',
    '-i', '../../lista-tools.ico',
    '--add-data=../../VERSION;.',
    '--add-data=../update/dist/update.exe;.',

])

print(f"Application built with version number {new_version}")
