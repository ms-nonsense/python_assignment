"""
Utility methods for this application
"""
import json

from pathlib import Path
from typing import Dict

script_location = Path(__file__).absolute().parent
file_location = script_location / 'conf/config.json'


def get_config() -> Dict:
    with open(file_location) as f:
        return json.load(f)
