import json
from pathlib import Path

RAW_FOLDER = Path("data/raw")
FIELDS = {"NOK_per_kWh", "EUR_per_kWh", "EXR", "time_start", "time_end"}


def load_files():
    files = sorted(RAW_FOLDER.glob("prices_*.json"))
    return [(file.name, json.loads(file.read_text(encoding="utf-8"))) for file in files]


def test_there_are_files():
    assert len(load_files()) > 0


def test_row_count():
    for name, rows in load_files():
        assert len(rows) in (23, 24, 25), name


def test_fields():
    for name, rows in load_files():
        for row in rows:
            assert FIELDS <= set(row), name


def test_no_duplicate_hours():
    for name, rows in load_files():
        hours = [row["time_start"] for row in rows]
        assert len(hours) == len(set(hours)), name
