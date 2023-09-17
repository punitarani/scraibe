"""scraibe"""

import os

import openai
from dotenv import load_dotenv

from config import PROJECT_DIR

load_dotenv(PROJECT_DIR.joinpath(".env"))

SUBJECT_ID = 10014354

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY, "OPENAI_API_KEY environment variable not set"
openai.api_key = OPENAI_API_KEY
