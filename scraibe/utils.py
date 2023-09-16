"""scraibe.utils.py"""

from pathlib import Path


def del_dir(dir_path: Path) -> None:
    """
    Delete a directory and its contents.

    Parameters
    ----------
    dir_path : Path
        The path to the directory to delete.
    """
    # Ensure the path is a directory
    if not dir_path.is_dir():
        raise ValueError(f"{dir_path} is not a directory.")

    # Recursively delete all files and subdirectories
    for item in dir_path.iterdir():
        if item.is_dir():
            delete_directory(item)  # Recurse into subdirectories
        else:
            item.unlink()  # Delete files

    # Delete the directory itself
    dir_path.rmdir()
