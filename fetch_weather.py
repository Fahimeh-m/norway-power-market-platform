import time
from datetime import date
from pathlib import Path

import requests

PLACES = {
    "NO1": (59.91, 10.75),  # Oslo
    "NO2": (58.15, 8.00),   # Kristiansand
    "NO3": (63.43, 10.40),  # Trondheim
    "NO4": (69.65, 18.96),  # Tromso
    "NO5": (60.39, 5.32),   # Bergen
}
HEADERS = {"User-Agent": "norway-power-market-platform github.com/Fahimeh-m"}
URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"


def get_json_with_retry(url, attempts=3, wait=10):
    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return response, response.json()
        except (requests.RequestException, ValueError) as error:
            if attempt == attempts:
                raise
            print(f"Attempt {attempt} failed: {error}. Retrying in {wait} s")
            time.sleep(wait)
            wait *= 2


def fetch_today():
    day = date.today().isoformat()
    folder = Path("data/raw")
    folder.mkdir(parents=True, exist_ok=True)

    for area, (lat, lon) in PLACES.items():
        path = folder / f"weather_{day}_{area}.json"
        if path.exists():
            print(f"Already have {path}")
            continue

        response, data = get_json_with_retry(URL.format(lat=lat, lon=lon))

        steps = data["properties"]["timeseries"]
        if len(steps) < 48:
            raise ValueError(f"{area} on {day}: {len(steps)} time steps")

        path.write_text(response.text, encoding="utf-8")
        print(f"Saved {path} ({len(steps)} time steps)")


if __name__ == "__main__":
    fetch_today()