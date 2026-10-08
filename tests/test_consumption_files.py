import json
from pathlib import Path

RAW_FOLDER = Path("data/raw")
AREAS = ["NO1", "NO2", "NO3", "NO4", "NO5"]
FIELDS = {"startTime", "endTime", "priceArea", "consumptionGroup", "quantityKwh"}


def load_files():
    result = []
    for file in sorted(RAW_FOLDER.glob("consumption_*.json")):
        data = json.loads(file.read_text(encoding="utf-8"))
        rows_by_area = {}
        for area in data["data"]:
            rows_by_area[area["id"]] = area["attributes"]["consumptionPerGroupMbaHour"]
        result.append((file.name, rows_by_area))
    return result


def test_there_are_files():
    assert len(load_files()) > 0


def test_row_count():
    for name, rows_by_area in load_files():
        for area in AREAS:
            assert len(rows_by_area.get(area, [])) in (115, 120, 125), f"{name} {area}"


def test_fields():
    for name, rows_by_area in load_files():
        for area in AREAS:
            for row in rows_by_area.get(area, []):
                assert FIELDS <= set(row), f"{name} {area}"


def test_no_duplicate_hours():
    for name, rows_by_area in load_files():
        for area in AREAS:
            keys = [(row["startTime"], row["consumptionGroup"]) for row in rows_by_area.get(area, [])]
            assert len(keys) == len(set(keys)), f"{name} {area}"
