from os import environ as env  # noqa
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent.parent.parent

load_dotenv(BASE_DIR / '../.env')
