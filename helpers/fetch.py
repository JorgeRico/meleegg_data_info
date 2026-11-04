import json
import re
from pathlib import Path
from typing import Optional

import requests

RAW_DATA_DIR = Path(__file__).resolve().parent.parent
DEFAULT_TOURNAMENT_URL = "https://melee.gg/Tournament/View/491103#standings"


def get_tournament_id(url: str) -> str:
    match = re.search(r"/Tournament/View/(\d+)", url)
    if match is None:
        raise ValueError(f"Invalid tournament url: {url}")
    return match.group(1)


def fetch_tournament_data(url: str = DEFAULT_TOURNAMENT_URL, file_name: Optional[str] = None) -> dict:
    tournament_id = get_tournament_id(url)
    file_name = file_name if file_name is not None else f"tournament_{tournament_id}.json"
    api_url = f"https://melee.gg/api/tournaments/{tournament_id}"
    response = requests.get(api_url)
    response.raise_for_status()
    data = response.json()
    (RAW_DATA_DIR / file_name).write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data
