import json
from pathlib import Path

FILES = sorted(Path("data/raw").glob("weather_*.json"))


def load_steps(file):
    text = file.read_text(encoding="utf-8")
    return json.loads(text)["properties"]["timeseries"]


def test_there_are_files():
    assert len(FILES) > 0


def test_time_step_count():
    for file in FILES:
        steps = load_steps(file)
        assert len(steps) >= 48, file.name


def test_fields():
    for file in FILES:
        for step in load_steps(file):
            details = step["data"]["instant"]["details"]
            assert "time" in step, file.name
            assert "air_temperature" in details, file.name
            assert "wind_speed" in details, file.name


def test_no_duplicate_times():
    for file in FILES:
        times = [step["time"] for step in load_steps(file)]
        assert len(times) == len(set(times)), file.name
