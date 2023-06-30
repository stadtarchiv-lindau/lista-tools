# Contents
* [DOWNLOAD AND INSTALLATION](#download-and-installation)
* [USAGE AND COMMANDS](#usage-and-commands)
  * [clean-filenames](#clean-filenames)
  * [droid-csv](#droid-csv)
  * [exdir](#exdir)
  * [force-update](#force-update)
  * [rename](#rename)
  * [version](#version)

# DOWNLOAD AND INSTALLATION
To download the latest version, click [here](https://github.com/stadtarchiv-lindau/lista-tools/releases/latest).

To install lista-tools, simply download the executable and move it to the location you want to store it. Be sure to [add lista-tools to PATH](https://gist.github.com/ScribbleGhost/752ec213b57eef5f232053e04f9d0d54), so you can run it from the command line.
# USAGE AND COMMANDS
General usage:
```
lista-tools [COMMAND] [ARGUMENT] --options
```
To get help in the command line pass the option `--help` without any arguments to get general help or after an argument to get help with that specific command.
## clean-filenames
Usage:
```
lista-tools clean-filenames
```
Cleans up all filenames in the working directory by substituting all non-alphanumerical characters with underscores, as well as replacing the german Umlaute with their counterparts; e.g. `ä → ae`

## droid-csv
Usage:
```
lista-tools droid-csv INPUT [OPTIONS]
```

This command converts csv files that droid outputs to be compatible with [this](https://github.com/stadtarchiv-lindau/lista-tools/releases/latest/download/template.xlsx) Excel template. 
```
 INPUT                           The name of the csv file you 
                                 want to convert
                                 
 -o, --output                    What the output file will be
                                 called. Pass this with the
                                 extension; e.g. -o 'done.csv'
                                 Defaults to 'output.csv'
                                 
 -F, --remove-folders            Additionally removes any rows
                                 that contain information on
                                 folders. Defaults to off
 ```

## exdir
Usage:
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

```
 -R, --no-recursion              Disables the recursive beha-
                                 viour and only extracts the
                                 first layer of folders.
```

## force-update
Usage:
```
lista-tools force-update
```

Opens the update dialogue, even if no newer version is available.
## rename
Usage:
```
lista-tools rename [OPTIONS]
```
Adds a prefix to all files and folders in the working directory.
```
 -S, --no-space                  Does not add a space after the
                                 prefix
 ```
## version
Usage:
```
lista-tools version
```
Prints version info