"""data/prepare.py"""

import gzip
import shutil
from pathlib import Path


def uncompress() -> None:
    """
    Uncompress .csv.gz files
    """

    folders = ["mimic-iv-demo/hosp", "mimic-iv-demo/icu"]

    for folder in folders:
        # Get all .csv.gz files in the folder
        files = Path(folder).glob("*.csv.gz")

        # Uncompress each file
        for file in files:
            with gzip.open(file, "rt") as f_in:
                content = f_in.read()  # Read the content from the compressed file
                print(
                    f"Content from {file}: {content[:100]}..."
                )  # Print first 100 characters

                with open(file.with_suffix("").with_suffix(".csv"), "wt") as f_out:
                    f_out.write(content)  # Write the content to the uncompressed file

            # Move the compressed file to the archive folder
            archive_folder = Path(folder).parent.joinpath(
                "archive", folder.split("/")[-1]
            )
            archive_folder.mkdir(parents=True, exist_ok=True)
            shutil.move(file, archive_folder.joinpath(file.name))
            print(f"Moved {file.name} to {archive_folder}.")


if __name__ == "__main__":
    uncompress()
