# ACIT4420-Final-Project

## Installation

Installation is relatively straight-forward: once the repository is cloned, simply run

```bash
python -m pip install .
```

to install the packages (`both TarjanPlanner`, and `FileOrganizer`).

## Tests

Unit tests can be run by calling:

```bash
python setup.py test
```

If all tests work, it should print `OK` at the end.

## Running TarjanPlanner

TarjanPlanner can be used to solve a version of the Traveling Salesman problem, allowing its user to find the ideal, fastest path to visit all their relatives. The package can be run by calling:

```bash
python -m TarjanPlanner
```

which will automatically drop the user in the main menu. From here, users will be able to import their relatives from a `.jsonl` file, add new ones manually from the console, and list all added relatives before they calculate the route. They can then calculate the route, and choose to either display it, save it to an `.svg` file, or both.

### Adding relatives

As mentioned above, relatives can be added in two ways, by file or by console. When adding a relative by file, a specific format must be followed:

```json
{"name": "Relative_0", "street_name": "street", "district": "district", "latitude": 0.0, "longitude": 0.0}
```

where all shown fields are required to be filled out for the program to work.

Additionally, the contacts *must* be stored in a valid `relatives.jsonl` file, in the `data` directory where the program is called from (that is to say, relatives must be stored at `./data/relatives.jsonl`).

### Adding modes of transport

Modes of transport (such as bus, train, etc.) must be added before the program is run: They are also stored in a `json` file, in the `data` directory, and are formatted like this:

```json
{
    "bus": {
        "speed": 40,
        "cost_per_km": 2,
        "transfer_time_min": 5
    },
    "train": {
        "speed": 80,
        "cost_per_km": 5,
        "transfer_time_min": 2
    },
    "bicycle": {
        "speed": 15,
        "cost_per_km": 0,
        "transfer_time_min": 1
    },
    "walking": {
        "speed": 5,
        "cost_per_km": 0,
        "transfer_time_min": 0
    }
}
```

Modes of transport can be added as needed, although their color will always be displayed as brown if so.

### Adding edges/routes

The routes between each relative (i.e. edges for each node) must also be manually added: these are stored as a `json` file in `data`, and are in the format:

```json
{
"0 5": "bus",
...
}
```

where the key is in the format: "<first> <second>" nodes, and the value is the transport method. The node values to be used are easy to determine: `0` is always the starting node (i.e. the user's location), while `1`, `2`, etc. are the relative's respective position (or line) in `relatives.jsonl`.

## Running the file organizer

The file organizer can be used to organize files based on their type and extension. File types (such as python files, executables, etc.) are stored in the `file_types.py` module, and can be extended at runtime by selecting the corresponding option in the main menu.

It can be run by calling:

```bash
python -m FileOrganizer
```

The program will assume that the directory the user calls it from is the one that is to be sorted, and will proceed to identify all files recursively (i.e. within the subdirectories as well), based on their extension. Files with incorrect/no extension cannot be recognized, and will not be touched by the program, as it assumes the user wishes to not sort them.

Once all registered file types have been found, a folder for each category (python, executables, video, etc.) will be created. Permission for the folder are set to give read/write access to the user running the package, and read access to everyone else.

Finally, the program sorts all files in their relevant folders, and returns to the main menu.

### Running the program multiple times

The program can be run multiple times if the user wishes (e.g., after adding a new file type), and will not resort already sorted files, unless their file type has been changed.

### Error handling

The package is written to be able to handle read and write permission errors: while it will not be able to deal with them, it will warn the user and simply not have any effect.

## Logging

Logging happens automatically during execution of both packages. Each will save to a log file with their own name, e.g. `TarjanPlanner.log` and `FileOrganizer.log`.

These programs are configured to both print all log `WARN` and above messages to console, and write *all* log messages (excluding `DEBUG` messages) to `TarjanPlanner.log` and `FileOrganizer.log`, for each respective package. These files have a maximum size of 3MB, before they are rotated and a new file is created. A maximum of three log files can exist simultaneously, and will be stored in the user's current directory (i.e. where the program is called).
