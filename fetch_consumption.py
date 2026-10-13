import sys
from datetime import date, timedelta
from pathlib import Path

import requests

AREAS = ["NO1", "NO2", "NO3", "NO4", "NO5"]
RAW_FOLDER = Path("data/raw")


def fetch_day(day):
    file = RAW_FOLDER / f"consumption_{day}.json"
    if file.exists():
        print(f"Already have {file}")
        return True

    next_day = date.fromisoformat(day) + timedelta(days=1)
    url = f"https://api.elhub.no/energy-data/v0/price-areas?dataset=CONSUMPTION_PER_GROUP_MBA_HOUR&startDate={day}&endDate={next_day}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    counts = {}
    for area in response.json()["data"]:
        counts[area["id"]] = len(area["attributes"]["consumptionPerGroupMbaHour"])

    if all(counts.get(area, 0) == 0 for area in AREAS):
        print(f"Not yet published: {day}")
        return False

    for area in AREAS:
        if counts.get(area) not in (115, 120, 125):
            raise ValueError(f"{area} on {day}: {counts.get(area)} rows")

    RAW_FOLDER.mkdir(parents=True, exist_ok=True)
    file.write_text(response.text, encoding="utf-8")
    print(f"Saved {file}")
    return True


if len(sys.argv) > 1:
    fetch_day(sys.argv[1])
else:
    for back in range(7, 1, -1):
        day = str(date.today() - timedelta(days=back))
        got_it = fetch_day(day)
        if back == 7 and not got_it:
            raise ValueError(f"{day} is still missing after 7 days")
