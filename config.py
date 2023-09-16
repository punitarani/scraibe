"""config.py"""

from pathlib import Path

PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR.joinpath("data")


# Create directories if they don't exist
DATA_DIR.mkdir(parents=False, exist_ok=True)
