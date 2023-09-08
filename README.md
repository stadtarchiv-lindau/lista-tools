# Contents
* [DOWNLOAD AND INSTALLATION](#download-and-installation)
* [USAGE AND COMMANDS](#usage-and-commands)
  * [General Options](#general-options)
  * [clean-filenames](#clean-filenames)
  * [droid-csv](#droid-csv)
  * [exdir](#exdir)
  * [rename](#rename)

# DOWNLOAD AND INSTALLATION
To download the latest version, click [here](https://github.com/stadtarchiv-lindau/lista-tools/releases/latest).

To install lista-tools, simply download the executable and move it to the location you want to store it. Be sure to [add lista-tools to PATH](https://gist.github.com/ScribbleGhost/752ec213b57eef5f232053e04f9d0d54), so you can run it from the command line.

# USAGE AND COMMANDS
```
lista-tools --options [COMMAND] [ARGUMENTS] --options
```
The general options passed before the command change the behaviour of the entire program, while the ones at the end only relate to that specific command. 

To get help in the command line pass the option `--help` without any arguments to get general help or after an argument to get help with that specific command.

## General Options
```
-l, --logging [none|error|warn|full|debug]
                                The level of verbosity of the script. 'none'
                                prints nothing, 'error' only errors, 'warn'
                                warnings and errors, 'full' prints
                                everything, 'debug' prints additional debug
                                info. When using 'none', 'error' or 'warn'
                                be sure to also use --noconfirm to avoid
                                issues with being asked for confirmation
-y, --noconfirm                 Automatically confirms all prompts
--target-dir DIRECTORY          The directory that the commands will be
                                executed in. If the option is not passed,
                                the directory in which you opened the script
                                will be used
-U, --force-update              Opens the update dialogue even if no newer
                                version is available
-v, --version                   Prints information about the current and
                                available version
-d, --debug                     Functionally identical to '-l debug'.
                                Implemented for nicer commands. Overrides
                                '-l'
--help                          Show this message and exit.
```

## clean-filenames
#### Usage:
```
lista-tools clean-filenames [OPTIONS]
```
Cleans up filenames by substituting all non-alphanumerical characters with underscores. Also replaces the German Umlaute with their alphanumerical counterparts (e.g. `ä → ae`).

## droid-csv
#### Usage:
```
lista-tools droid-csv INPUT [OPTIONS]
```
Formats a csv file made by DROID to fit in the [LIStA Excel Template](https://github.com/stadtarchiv-lindau/lista-tools/releases/latest/download/template.xlsx).

INPUT is the path to the input file.

#### Options:

```
-o, --output TEXT               The name of the output file, defaults to
                                'output.csv'
--keep-folders / -F, --remove-folders
                                Removes all rows containing information on
                                folders, defaults to '--keep-folders'
--help                          Show this message and exit.
```

## exdir
#### Usage:
```
lista-tools exdir [OPTIONS]
```
Extracts all folders inside the working directory and adds the name of the parent folder as a prefix to extracted element. This process is repeated until there are only files left in the working directory.
<details>
<summary>Example</summary>

```
BEFORE:                       AFTER:
   
exdir/                        exdir/
├── programming/              ├── PROGRAMMING_ JAVA_ class.class
│   ├── java/                 ├── PROGRAMMING_ JAVA_ program.java
│   │   ├── class.class       ├── PROGRAMMING_ PYTHON_ PROJECT1_ _a.py
│   │   └── program.java      ├── PROGRAMMING_ PYTHON_ PROJECT1_ _b.py 
│   └── python/               ├── PROGRAMMING_ PYTHON_ PROJECT1_ _c.py
│       ├── project1/         ├── PROGRAMMING_ PYTHON_ PROJECT1_ _d.py
│       │   ├── _a.py         ├── SONGS_ FLAC_ song1.flac
│       │   └── _b.py         ├── SONGS_ FLAC_ song2.flac
│       └── project2/         ├── SONGS_ FLAC_ song3.flac
│           ├── _c.py         ├── SONGS_ FLAC_ song4.flac
│           └── _d.py         ├── SONGS_ FLAC_ song5.flac
├── songs/                    ├── SONGS_ MP3_ song10.mp3
│   ├── FLAC/                 ├── SONGS_ MP3_ song6.mp3
│   │   ├── song1.flac        ├── SONGS_ MP3_ song7.mp3
│   │   ├── song2.flac        ├── SONGS_ MP3_ song8.mp3
│   │   ├── song3.flac        ├── SONGS_ MP3_ song9.mp3
│   │   ├── song4.flac        ├── style_sheet.css
│   │   └── song5.flac        ├── VIDEOS_ thumbnail1.jpeg
│   └── MP3/                  ├── VIDEOS_ thumbnail2.tiff
│       ├── song10.mp3        ├── VIDEOS_ video1.mp4
│       ├── song6.mp3         ├── VIDEOS_ video2.m4a
│       ├── song7.mp3         └── website.html
│       ├── song8.mp3      
│       └── song9.mp3
├── style_sheet.css
├── videos/
│   ├── thumbnail1.jpeg
│   ├── thumbnail2.tiff
│   ├── video1.mp4
│   └── video2.m4a
└── website.html
```
</details>

#### Options:

```
--recursion / -R, --no-recursion
                                Toggles recursive behaviour. If '--no-
                                recursion' is passed, only the top layer of
                                directories will be , defaults to '--
                                recursion'
--help                          Show this message and exit.
```

## rename
#### Usage:
```
lista-tools rename [OPTIONS] PREFIX
```
Adds the passed prefix to all elements in the target directory.
