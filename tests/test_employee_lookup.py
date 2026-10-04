from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.employee_lookup import escape_like, looks_like_id, sync_status


def test_escape_like_treats_wildcards_literally():
    assert escape_like("50%_off") == "50\\%\\_off"
    assert escape_like("a\\b") == "a\\\\b"
    assert escape_like("Priya") == "Priya"


def test_looks_like_id():
    assert looks_like_id("E000123")
    assert looks_like_id(" e1a2b3c4d ")
    assert not looks_like_id("Priya")
    assert not looks_like_id("123")


RECORD = {"department_id": 2, "department_name": "Engineering", "role": "Analyst"}


def _history(rows):
    return pd.DataFrame(rows, columns=["department_id", "department_name", "role", "is_current"])


def test_sync_ok_after_department_change():
    hist = _history([(5, "Human Resources", "Analyst", 0), (2, "Engineering", "Analyst", 1)])
    status = sync_status(RECORD, hist)
    assert status["state"] == "ok"
    assert "2 versions" in status["text"]


def test_sync_detects_stale_warehouse():
    hist = _history([(5, "Human Resources", "Analyst", 1)])
    status = sync_status(RECORD, hist)
    assert status["state"] == "differs"
    assert "Human Resources" in status["text"] and "Engineering" in status["text"]


def test_sync_missing_when_not_loaded():
    assert sync_status(RECORD, _history([]))["state"] == "missing"
