"""scraibe/db.py"""

import os

import iris
from dotenv import load_dotenv

from config import PROJECT_DIR

load_dotenv(PROJECT_DIR.joinpath(".env"))

IRIS_HOST = os.getenv("IRIS_HOST")
IRIS_PORT = os.getenv("IRIS_PORT")
IRIS_NAME = os.getenv("IRIS_NAME")
IRIS_USER = os.getenv("IRIS_USER")
IRIS_PASS = os.getenv("IRIS_PASS")

assert IRIS_HOST, "IRIS_HOST environment variable not set"
assert IRIS_PORT, "IRIS_PORT environment variable not set"
assert IRIS_NAME, "IRIS_NAME environment variable not set"
assert IRIS_USER, "IRIS_USER environment variable not set"
assert IRIS_PASS, "IRIS_PASS environment variable not set"


def connect() -> iris.IRISConnection:
    """
    Connect to InterSystems IRIS
    """
    return iris.connect(f"{IRIS_HOST}:{IRIS_PORT}/{IRIS_NAME}", IRIS_USER, IRIS_PASS)


if __name__ == "__main__":
    conn = connect()

    # Create a cursor
    cur = conn.cursor()

    # Get all tables in InterSystems IRIS SQL
    cur.execute(
        """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE';
        """
    )
    tables = cur.fetchall()
    for table in tables:
        print(table[0])

    conn.close()
