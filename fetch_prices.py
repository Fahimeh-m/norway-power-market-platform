import os
import sys
from datetime import date

import requests

AREAS = ["NO1", "NO2", "NO3", "NO4", "NO5"]


def fetch_day(day):
    os.makedirs("data/raw/prices", exist_ok=True)
    for area in AREAS:
        url = f"https://www.hvakosterstrommen.no/api/v1/prices/{day[:4]}/{day[5:]}_{area}.json"
        response = requests.get(url)
        response.raise_for_status()
        rows = response.json()
        if len(rows) not in (23, 24, 25):
            raise ValueError(f"{area} {day}: unexpected row count {len(rows)}")
        with open(f"data/raw/prices/prices_{day}_{area}.json", "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"saved {area} {day}: {len(rows)} rows")


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    fetch_day(day)
