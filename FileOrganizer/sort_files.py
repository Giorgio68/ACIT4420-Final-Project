"""
Module containing the logic used to sort files based on type
"""

import re
import os
import shutil
from pathlib import Path
from typing import Optional
from .file_types import files
from .logger import get_logger


_logger = get_logger()


def _find_identify_all_files(path: str | Path) -> None:
    """
    Find all files listed as available types, and add them to the `types` object

    :param path: Where to search for files to sort
    """
    for typ, data in files.items():
        extensions = data["extension"]
        data["files"] = []

        for extension in extensions:
            try:
                for directory in os.walk(path):
                    data["files"].extend(
                        [
                            f"{directory[0]}\\{file}"
                            for file in directory[2]
                            if re.search(
                                r"\.{}$".format(extension), file  # pylint: disable=consider-using-f-string
                            )
                        ]
                    )

            except PermissionError:
                _logger.error("No read access to directory %s", path)
                raise

        _logger.debug("Found files %s for category %s", data["files"], typ)


def _make_dirs_by_type(path: str | Path) -> None:
    """
    Create directories by file type to store all sorted files

    :param path: Where to create the directories
    """

    if not isinstance(path, Path):
        path = Path(path)

    for typ in files:
        try:
            # 0o644 is read/write for us, read for everyone else
            (path / typ).mkdir(mode=0o644, exist_ok=True)

            _logger.debug("Created folder %s", path / typ)

        except OSError:
            _logger.exception(
                "The OS denied access when trying to create folder %s, skipping...", typ
            )


def _sort_files_in_dir(path: str | Path) -> None:
    """
    Sort all previously found files in their directories

    :param path: The root path to move all files into
    """
    for typ, data in files.items():
        unsorted_files = data["files"]

        for file in unsorted_files:
            try:
                shutil.move(Path(file), path / typ)

            except shutil.Error:
                _logger.warning("File %s is already sorted, skipping...", file)

            except OSError:
                _logger.exception(
                    "OS denied access when trying to move file %s to %s, skipping...",
                    file,
                    path / typ,
                )


def sort(directory: Optional[str | Path] = None) -> None:
    """
    Sorts all files into folders based on their extension. E.g. python files will be sorted in
    `python`, mp4 files in `video`, and so on
    """

    if not directory:
        directory = Path(".")

    if not isinstance(directory, Path):
        directory = Path(directory)

    if not directory.exists():
        _logger.error("Non-existent directory was passed: %s", directory)
        return

    _find_identify_all_files(directory)
    _make_dirs_by_type(directory)
    _sort_files_in_dir(directory)

    _logger.info("Sorted all files")
